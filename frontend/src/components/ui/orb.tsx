import React, { useRef, useEffect, useMemo } from 'react';
import { Canvas, useFrame, extend } from '@react-three/fiber';
import * as THREE from 'three';

// Extend Three.js elements for React Three Fiber
extend(THREE);

type AgentState = null | "thinking" | "listening" | "talking";

interface OrbProps {
  colors?: [string, string];
  colorsRef?: React.RefObject<[string, string]>;
  resizeDebounce?: number;
  seed?: number;
  agentState?: AgentState;
  volumeMode?: "auto" | "manual";
  manualInput?: number;
  manualOutput?: number;
  inputVolumeRef?: React.RefObject<number>;
  outputVolumeRef?: React.RefObject<number>;
  getInputVolume?: () => number;
  getOutputVolume?: () => number;
  className?: string;
}

const vertexShader = `
  varying vec2 vUv;
  varying vec3 vPosition;
  
  void main() {
    vUv = uv;
    vPosition = position;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const fragmentShader = `
  uniform float uTime;
  uniform vec3 uColor1;
  uniform vec3 uColor2;
  uniform float uInputVolume;
  uniform float uOutputVolume;
  uniform float uAgentState;
  
  varying vec2 vUv;
  varying vec3 vPosition;
  
  void main() {
    vec2 center = vec2(0.5, 0.5);
    float dist = distance(vUv, center);
    
    // Base animation
    float wave = sin(dist * 10.0 - uTime * 2.0) * 0.5 + 0.5;
    
    // Audio reactivity
    float audioEffect = (uInputVolume + uOutputVolume) * 0.5;
    wave += audioEffect * 0.3;
    
    // Agent state effect
    float stateEffect = uAgentState * 0.2;
    wave += stateEffect;
    
    // Color mixing
    vec3 color = mix(uColor1, uColor2, wave);
    
    // Fade edges
    float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
    
    gl_FragColor = vec4(color, alpha);
  }
`;

function OrbMesh({ 
  colors, 
  agentState, 
  getInputVolume, 
  getOutputVolume,
  volumeMode,
  manualInput,
  manualOutput,
  inputVolumeRef,
  outputVolumeRef
}: Omit<OrbProps, 'className' | 'resizeDebounce' | 'seed' | 'colorsRef'>) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uColor1: { value: new THREE.Color(colors?.[0] || "#CADCFC") },
    uColor2: { value: new THREE.Color(colors?.[1] || "#A0B9D1") },
    uInputVolume: { value: 0 },
    uOutputVolume: { value: 0 },
    uAgentState: { value: 0 }
  }), []);

  useEffect(() => {
    uniforms.uColor1.value.set(colors?.[0] || "#CADCFC");
    uniforms.uColor2.value.set(colors?.[1] || "#A0B9D1");
  }, [colors, uniforms]);

  useFrame((state) => {
    if (!meshRef.current) return;
    
    uniforms.uTime.value = state.clock.elapsedTime;
    
    // Update volume
    if (volumeMode === "manual") {
      uniforms.uInputVolume.value = manualInput || 0;
      uniforms.uOutputVolume.value = manualOutput || 0;
    } else {
      if (inputVolumeRef?.current !== undefined) {
        uniforms.uInputVolume.value = inputVolumeRef.current;
      } else if (getInputVolume) {
        uniforms.uInputVolume.value = getInputVolume();
      }
      
      if (outputVolumeRef?.current !== undefined) {
        uniforms.uOutputVolume.value = outputVolumeRef.current;
      } else if (getOutputVolume) {
        uniforms.uOutputVolume.value = getOutputVolume();
      }
    }
    
    // Update agent state
    const stateValue = 
      agentState === "thinking" ? 0.3 :
      agentState === "listening" ? 0.6 :
      agentState === "talking" ? 1.0 : 0;
    uniforms.uAgentState.value = stateValue;
    
    // Gentle rotation
    meshRef.current.rotation.z += 0.001;
  });

  return (
    // @ts-ignore - React Three Fiber types
    <mesh ref={meshRef}>
      <sphereGeometry args={[1, 64, 64]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        transparent
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

export function Orb({
  colors = ["#CADCFC", "#A0B9D1"],
  agentState = null,
  volumeMode = "auto",
  manualInput,
  manualOutput,
  inputVolumeRef,
  outputVolumeRef,
  getInputVolume,
  getOutputVolume,
  className = ""
}: OrbProps) {
  return (
    <div className={className} style={{ width: '100%', height: '100%' }}>
      {/* @ts-ignore - React Three Fiber types */}
      <Canvas camera={{ position: [0, 0, 3], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <OrbMesh
          colors={colors}
          agentState={agentState}
          volumeMode={volumeMode}
          manualInput={manualInput}
          manualOutput={manualOutput}
          inputVolumeRef={inputVolumeRef}
          outputVolumeRef={outputVolumeRef}
          getInputVolume={getInputVolume}
          getOutputVolume={getOutputVolume}
        />
      </Canvas>
    </div>
  );
}
