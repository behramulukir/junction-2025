import { useState, useEffect } from 'react';
import { useConversation } from '@elevenlabs/react';
import { Orb } from './ui/orb';

type AgentState = null | "thinking" | "listening" | "talking";

const AGENT_ID = import.meta.env.VITE_ELEVENLABS_AGENT_ID || 'agent_7801ka4a5pnff3rsfcw0c2m9g572';
const API_KEY = import.meta.env.VITE_ELEVENLABS_API_KEY;

interface VoiceAssistantProps {
  context?: {
    viewMode?: string;
    selectedCategory?: string | null;
    categoryDescription?: string;
    selectedSubCategory?: string | null;
    subCategoryDescription?: string;
    selectedIssue?: any;
    selectedRequirement?: any;
    totalIssues?: number;
    totalRequirements?: number;
  };
}

export function VoiceAssistant({ context }: VoiceAssistantProps) {
  const [agentState, setAgentState] = useState<AgentState>(null);
  const [isActive, setIsActive] = useState(false);
  const [inputVolume, setInputVolume] = useState(0);
  const [outputVolume, setOutputVolume] = useState(0);
  const [signedUrl, setSignedUrl] = useState<string | null>(null);

  const conversation = useConversation({
    onConnect: () => {
      console.log('Connected to ElevenLabs');
      setIsActive(true);
      setAgentState('listening');
    },
    onDisconnect: () => {
      console.log('Disconnected from ElevenLabs');
      setIsActive(false);
      setAgentState(null);
      setInputVolume(0);
      setOutputVolume(0);
    },
    onError: (error) => {
      console.error('Conversation error:', error);
      setIsActive(false);
      setAgentState(null);
    },
    onModeChange: (mode) => {
      console.log('Mode changed:', mode);
      if (mode.mode === 'speaking') {
        setAgentState('talking');
      } else if (mode.mode === 'listening') {
        setAgentState('listening');
      } else {
        setAgentState('listening');
      }
    },
    onMessage: (message) => {
      console.log('Message:', message);
    },
  });

  // Get signed URL for the agent
  const getSignedUrl = async () => {
    try {
      if (!API_KEY) {
        throw new Error('ElevenLabs API key is not configured');
      }
      
      const response = await fetch(`https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id=${AGENT_ID}`, {
        method: 'GET',
        headers: {
          'xi-api-key': API_KEY,
        },
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Failed to get signed URL:', response.status, errorText);
        throw new Error(`Failed to get signed URL: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Got signed URL successfully');
      return data.signed_url;
    } catch (error) {
      console.error('Error getting signed URL:', error);
      throw error;
    }
  };

  // Build context string for the agent
  const buildContextString = () => {
    if (!context) return '';
    
    let contextStr = 'Current Dashboard Context:\n\n';
    
    if (context.viewMode) {
      contextStr += `View Mode: ${context.viewMode}\n\n`;
    }
    
    // Category Context
    if (context.selectedCategory) {
      contextStr += `Category: ${context.selectedCategory}\n`;
      if (context.categoryDescription) {
        contextStr += `Category Description: ${context.categoryDescription}\n`;
      }
      contextStr += '\n';
    }
    
    // Sub-Category Context
    if (context.selectedSubCategory) {
      contextStr += `Sub-Category: ${context.selectedSubCategory}\n`;
      if (context.subCategoryDescription) {
        contextStr += `Sub-Category Description: ${context.subCategoryDescription}\n`;
      }
      contextStr += '\n';
    }
    
    // Issue Details (complete)
    if (context.viewMode === 'issues' && context.selectedIssue) {
      const issue = context.selectedIssue;
      contextStr += `Currently Viewing Issue:\n`;
      contextStr += `- ID: ${issue.id}\n`;
      contextStr += `- Type: ${issue.type}\n`;
      contextStr += `- Regulations Involved: ${issue.reg1} × ${issue.reg2}\n`;
      contextStr += `- Description: ${issue.description}\n`;
      
      if (issue.severity) {
        contextStr += `- Severity: ${issue.severity}\n`;
      }
      
      if (issue.confidence) {
        contextStr += `- Confidence Score: ${(issue.confidence * 100).toFixed(0)}%\n`;
      }
      
      // Add excerpts/requirements
      if (issue.type === 'contradiction' && issue.requirement1 && issue.requirement2) {
        contextStr += `\nConflicting Requirements:\n`;
        contextStr += `${issue.reg1}: "${issue.requirement1}"\n`;
        contextStr += `${issue.reg2}: "${issue.requirement2}"\n`;
      } else if (issue.type === 'overlap' && issue.excerpt1 && issue.excerpt2) {
        contextStr += `\nExcerpts:\n`;
        contextStr += `${issue.reg1}: "${issue.excerpt1}"\n`;
        contextStr += `${issue.reg2}: "${issue.excerpt2}"\n`;
      }
      
      contextStr += '\n';
    }
    
    // Requirement Details (complete)
    if (context.viewMode === 'requirements' && context.selectedRequirement) {
      const req = context.selectedRequirement;
      contextStr += `Currently Viewing Requirement:\n`;
      contextStr += `- Regulation: ${req.regulation}\n`;
      contextStr += `- Sub-Category: ${req.subCategory}\n`;
      contextStr += `- Full Text: "${req.text}"\n\n`;
    }
    
    // Summary stats
    if (context.totalIssues !== undefined) {
      contextStr += `Total Issues in Current View: ${context.totalIssues}\n`;
    }
    
    if (context.totalRequirements !== undefined) {
      contextStr += `Total Requirements in Current View: ${context.totalRequirements}\n`;
    }
    
    return contextStr;
  };

  const toggleConversation = async () => {
    if (isActive) {
      await conversation.endSession();
      setSignedUrl(null);
    } else {
      try {
        // Get signed URL first
        console.log('Getting signed URL for agent:', AGENT_ID);
        const url = await getSignedUrl();
        
        if (!url) {
          alert('Could not connect to the agent. The agent may require authentication.');
          return;
        }
        
        console.log('Starting session with signed URL');
        setSignedUrl(url);
        
        // Build context for the agent
        const contextString = buildContextString();
        console.log('Sending context to agent via dynamic variable:', contextString);
        
        // Start the session with dynamic variables
        await conversation.startSession({
          signedUrl: url,
          dynamicVariables: {
            context: contextString,
          },
        });
      } catch (error) {
        console.error('Failed to start conversation:', error);
        alert('Could not start conversation. The agent may require an API key. Please check the console for details.');
      }
    }
  };
  
  // Send context updates during conversation
  useEffect(() => {
    if (isActive && context) {
      const contextString = buildContextString();
      console.log('Updating context via contextual update:', contextString);
      // Send context update to the agent during conversation
      conversation.sendContextualUpdate(contextString);
    }
  }, [context, isActive]);

  // Monitor audio levels
  useEffect(() => {
    if (!isActive) return;

    const interval = setInterval(() => {
      try {
        const input = conversation.getInputVolume();
        const output = conversation.getOutputVolume();
        
        setInputVolume(input);
        setOutputVolume(output);
      } catch (error) {
        // Ignore errors
      }
    }, 50);

    return () => clearInterval(interval);
  }, [isActive, conversation]);

  return (
    <div className="absolute top-6 right-6 z-50 pointer-events-none">
      <div 
        className="w-24 h-24 cursor-pointer transition-transform hover:scale-105 pointer-events-auto"
        onClick={toggleConversation}
        title={isActive ? 'Click to end conversation' : 'Click to start conversation'}
      >
        <Orb
          agentState={agentState}
          volumeMode="manual"
          manualInput={inputVolume}
          manualOutput={outputVolume}
          colors={
            agentState === "talking" ? ["#4ECDC4", "#44A08D"] :
            agentState === "listening" ? ["#667eea", "#764ba2"] :
            agentState === "thinking" ? ["#f093fb", "#f5576c"] :
            ["#CADCFC", "#A0B9D1"]
          }
        />
      </div>
    </div>
  );
}
