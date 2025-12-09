'use client';

import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { AnimatePresence, motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
    isStreaming?: boolean;
}

const INITIAL_MESSAGES: Message[] = [
    {
        id: '1',
        text: 'Bonjour ! Je suis l\'assistant Ticket Zen. Comment puis-je vous aider aujourd\'hui ?',
        sender: 'bot',
        timestamp: new Date(),
    },
];

export default function Chatbot() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleSendMessage = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!inputValue.trim() || isTyping) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            text: inputValue,
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        const currentInput = inputValue;
        setInputValue('');
        setIsTyping(true);

        // Create a temporary bot message for streaming
        const botMessageId = (Date.now() + 1).toString();
        const botMessage: Message = {
            id: botMessageId,
            text: '',
            sender: 'bot',
            timestamp: new Date(),
            isStreaming: true,
        };

        setMessages((prev) => [...prev, botMessage]);

        try {
            const history = messages.map(m => ({
                sender: m.sender,
                text: m.text
            }));

            // Abort previous request if any
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }

            abortControllerRef.current = new AbortController();

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: currentInput,
                    history: history
                }),
                signal: abortControllerRef.current.signal,
            });

            if (!response.ok) {
                throw new Error('Network error');
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) {
                throw new Error('No reader available');
            }

            let accumulatedText = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);

                        if (data === '[DONE]') {
                            setMessages((prev) =>
                                prev.map((msg) =>
                                    msg.id === botMessageId
                                        ? { ...msg, isStreaming: false }
                                        : msg
                                )
                            );
                            break;
                        }

                        try {
                            const parsed = JSON.parse(data);
                            if (parsed.text) {
                                accumulatedText += parsed.text;
                                setMessages((prev) =>
                                    prev.map((msg) =>
                                        msg.id === botMessageId
                                            ? { ...msg, text: accumulatedText }
                                            : msg
                                    )
                                );
                            }
                        } catch (e) {
                            // Ignore parse errors for incomplete chunks
                            void e;
                        }
                    }
                }
            }

        } catch (error) {
            if (error instanceof Error && error.name === 'AbortError') {
                return; // Request was aborted, ignore
            }

            console.error('Chat error:', error);
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === botMessageId
                        ? {
                            ...msg,
                            text: "Désolé, je rencontre des difficultés pour me connecter. Veuillez réessayer plus tard.",
                            isStreaming: false,
                        }
                        : msg
                )
            );
        } finally {
            setIsTyping(false);
            abortControllerRef.current = null;
        }
    };

    return (
        <>
            {/* Floating Button */}
            <motion.button
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setIsOpen(!isOpen)}
                className={cn(
                    "fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-colors",
                    isOpen ? "bg-red-500 hover:bg-red-600" : "bg-blue-600 hover:bg-blue-700"
                )}
            >
                {isOpen ? (
                    <X className="w-6 h-6 text-white" />
                ) : (
                    <MessageCircle className="w-6 h-6 text-white" />
                )}
            </motion.button>

            {/* Chat Window */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="fixed bottom-24 right-6 z-50 w-[90vw] md:w-[380px] max-h-[600px] h-[70vh] flex flex-col"
                    >
                        <Card className="flex flex-col h-full shadow-2xl border-0 overflow-hidden">
                            {/* Header */}
                            <div className="bg-blue-600 p-4 text-white flex items-center gap-3 shrink-0">
                                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                                    <Bot className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h3 className="font-bold">Assistant Ticket Zen</h3>
                                    <div className="flex items-center gap-1.5">
                                        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                                        <span className="text-xs text-blue-100">En ligne</span>
                                    </div>
                                </div>
                            </div>

                            {/* Messages Area */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
                                {messages.map((msg) => (
                                    <div
                                        key={msg.id}
                                        className={cn(
                                            "flex w-full",
                                            msg.sender === 'user' ? "justify-end" : "justify-start"
                                        )}
                                    >
                                        <div
                                            className={cn(
                                                "max-w-[80%] p-3 rounded-2xl text-sm shadow-sm",
                                                msg.sender === 'user'
                                                    ? "bg-blue-600 text-white rounded-tr-none"
                                                    : "bg-white text-slate-800 border border-slate-100 rounded-tl-none"
                                            )}
                                        >
                                            {msg.sender === 'bot' ? (
                                                <div className="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0">
                                                    <ReactMarkdown
                                                        remarkPlugins={[remarkGfm]}
                                                        components={{
                                                            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                                                            ul: ({ children }) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
                                                            ol: ({ children }) => <ol className="list-decimal pl-4 mb-2">{children}</ol>,
                                                            li: ({ children }) => <li className="mb-1">{children}</li>,
                                                            strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                                                            em: ({ children }) => <em className="italic">{children}</em>,
                                                            code: ({ children }) => <code className="bg-slate-100 px-1 rounded text-xs">{children}</code>,
                                                        }}
                                                    >
                                                        {msg.text || ' '}
                                                    </ReactMarkdown>
                                                    {msg.isStreaming && (
                                                        <span className="inline-block w-1 h-4 bg-slate-400 animate-pulse ml-0.5" />
                                                    )}
                                                </div>
                                            ) : (
                                                msg.text
                                            )}
                                            <div
                                                className={cn(
                                                    "text-[10px] mt-1 opacity-70",
                                                    msg.sender === 'user' ? "text-blue-100" : "text-slate-400"
                                                )}
                                            >
                                                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </div>
                                        </div>
                                    </div>
                                ))}

                                {isTyping && messages[messages.length - 1]?.sender !== 'bot' && (
                                    <div className="flex justify-start">
                                        <div className="bg-white border border-slate-100 p-3 rounded-2xl rounded-tl-none shadow-sm flex gap-1">
                                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            {/* Input Area */}
                            <div className="p-4 bg-white border-t border-slate-100 shrink-0">
                                <form onSubmit={handleSendMessage} className="flex gap-2">
                                    <Input
                                        value={inputValue}
                                        onChange={(e) => setInputValue(e.target.value)}
                                        placeholder="Posez votre question..."
                                        className="flex-1 bg-slate-50 border-slate-200 focus-visible:ring-blue-600"
                                        disabled={isTyping}
                                    />
                                    <Button
                                        type="submit"
                                        size="icon"
                                        className="bg-blue-600 hover:bg-blue-700 shrink-0"
                                        disabled={!inputValue.trim() || isTyping}
                                    >
                                        <Send className="w-4 h-4" />
                                    </Button>
                                </form>
                            </div>
                        </Card>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
