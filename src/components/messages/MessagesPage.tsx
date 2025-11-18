import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageSquare, 
  Search, 
  Plus, 
  Send, 
  Paperclip, 
  Smile, 
  Info
} from 'lucide-react';

interface Message {
  id: string;
  senderId: string;
  senderName: string;
  content: string;
  timestamp: string;
  read: boolean;
}

interface Conversation {
  id: string;
  participants: {
    id: string;
    name: string;
    role: string;
    online: boolean;
  }[];
  lastMessage: Message;
  unreadCount: number;
}

export const MessagesPage: React.FC = () => {
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [newMessage, setNewMessage] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // TODO: Replace with API call to fetch conversations from backend
  const [conversations] = useState<Conversation[]>([]);

  // TODO: Replace with API call to fetch messages from backend
  const [messages, setMessages] = useState<{ [conversationId: string]: Message[] }>({});

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return date.toLocaleDateString();
  };

  const selectedConversationData = conversations.find(c => c.id === selectedConversation);
  const conversationMessages = selectedConversation ? messages[selectedConversation] || [] : [];

  const sendMessage = () => {
    if (!newMessage.trim() || !selectedConversation) return;
    
    const newMsg: Message = {
      id: Date.now().toString(),
      senderId: '1',
      senderName: 'You',
      content: newMessage.trim(),
      timestamp: new Date().toISOString(),
      read: true
    };

    setMessages(prev => ({
      ...prev,
      [selectedConversation]: [...(prev[selectedConversation] || []), newMsg]
    }));
    
    setNewMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversationMessages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [newMessage]);

  return (
    <div className="h-[calc(100vh-2rem)] flex bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Conversations Sidebar */}
      <div className="w-80 border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold text-gray-900">Messages</h1>
            <button 
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="New Conversation"
            >
              <Plus className="h-5 w-5" />
            </button>
          </div>
          
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 ? (
            <div className="flex items-center justify-center h-full p-8">
              <div className="text-center">
                <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No conversations yet</h3>
                <p className="text-gray-600 text-sm">Start a conversation with your instructors or classmates</p>
              </div>
            </div>
          ) : (
            conversations
              .filter(conversation => {
                const otherParticipant = conversation.participants.find(p => p.name !== 'You');
                return otherParticipant?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                       conversation.lastMessage.content.toLowerCase().includes(searchTerm.toLowerCase());
              })
              .map((conversation) => {
            const otherParticipant = conversation.participants.find(p => p.name !== 'You');
            
            return (
              <button
                key={conversation.id}
                onClick={() => setSelectedConversation(conversation.id)}
                className={`w-full p-4 text-left hover:bg-gray-50 border-b border-gray-100 ${
                  selectedConversation === conversation.id ? 'bg-blue-50 border-r-2 border-r-blue-500' : ''
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-medium">
                      {otherParticipant?.name.charAt(0).toUpperCase()}
                    </div>
                    {otherParticipant?.online && (
                      <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium text-gray-900 truncate">
                        {otherParticipant?.name}
                      </h3>
                      <span className="text-xs text-gray-500">
                        {formatTimestamp(conversation.lastMessage.timestamp)}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between mt-1">
                      <p className="text-sm text-gray-600 truncate">
                        {conversation.lastMessage.content}
                      </p>
                      {conversation.unreadCount > 0 && (
                        <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                          {conversation.unreadCount}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </button>
            );
          })
          )}
        </div>
      </div>

      {/* Chat Area */}
      {selectedConversationData ? (
        <div className="flex-1 flex flex-col">
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-medium">
                  {selectedConversationData.participants.find(p => p.name !== 'You')?.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h2 className="font-medium text-gray-900">
                    {selectedConversationData.participants.find(p => p.name !== 'You')?.name}
                  </h2>
                  <p className="text-sm text-gray-500">
                    {selectedConversationData.participants.find(p => p.name !== 'You')?.online ? 'Online' : 'Offline'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg" title="Conversation Info">
                  <Info className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4" id="messages-container">
            {conversationMessages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No messages yet. Start the conversation!</p>
                </div>
              </div>
            ) : (
              conversationMessages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.senderId === '1' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                    message.senderId === '1'
                      ? 'bg-blue-600 text-white rounded-br-md'
                      : 'bg-gray-100 text-gray-900 rounded-bl-md'
                  } shadow-sm`}>
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    <p className={`text-xs mt-2 ${
                      message.senderId === '1' ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {formatTimestamp(message.timestamp)}
                    </p>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 border-t border-gray-200">
            <div className="flex items-end gap-3">
              <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                <Paperclip className="h-5 w-5" />
              </button>
              
              <div className="flex-1">
                <textarea
                  ref={textareaRef}
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type a message... (Press Enter to send)"
                  rows={1}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none max-h-32 overflow-y-auto"
                />
              </div>

              <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                <Smile className="h-5 w-5" />
              </button>
              
              <button
                onClick={sendMessage}
                disabled={!newMessage.trim()}
                className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Select a conversation</h3>
            <p className="text-gray-600">Choose a conversation from the sidebar to start messaging</p>
          </div>
        </div>
      )}
    </div>
  );
};