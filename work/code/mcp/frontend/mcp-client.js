/**
 * MCP WebSocket Client for Frontend Testing
 * Handles real WebSocket connections to the MCP server with proper protocol
 */

class MCPClient {
    constructor(serverUrl = 'ws://localhost:8765') {
        this.serverUrl = serverUrl;
        this.ws = null;
        this.isConnected = false;
        this.messageId = 0;
        this.pendingRequests = new Map();
        this.onMessage = null;
        this.onStatusChange = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
    }

    async connect() {
        return new Promise((resolve, reject) => {
            try {
                this.log('Attempting to connect to MCP server...', 'info');
                
                // Create WebSocket with fallback for browser compatibility
                try {
                    // Try with MCP subprotocol first (standard)
                    this.ws = new WebSocket(this.serverUrl, ['mcp']);
                } catch (e) {
                    this.log('MCP subprotocol not supported, trying without...', 'warning');
                    // Fallback for browsers that don't support subprotocols properly
                    this.ws = new WebSocket(this.serverUrl);
                }
                
                this.ws.onopen = () => {
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    clearTimeout(connectionTimeout); // Clear the timeout
                    this.notifyStatusChange(true, 'Connected to MCP Server');
                    this.log('WebSocket connection established', 'success');
                    
                    // Send MCP initialization and return the response
                    this.initializeMCP().then((initResponse) => {
                        resolve(initResponse);
                    }).catch(reject);
                };

                this.ws.onclose = (event) => {
                    this.isConnected = false;
                    
                    // Only log and attempt reconnection if this was an unexpected closure
                    if (event.code !== 1000 && event.code !== 1001) {
                        this.notifyStatusChange(false, `Connection lost (${event.code})`);
                        this.log(`WebSocket connection lost: ${event.code} - ${event.reason || 'Unknown reason'}`, 'warning');
                        
                        // Attempt reconnection if not intentional and within limits
                        if (this.reconnectAttempts < this.maxReconnectAttempts) {
                            this.attemptReconnect();
                        }
                    } else {
                        this.notifyStatusChange(false, 'Disconnected');
                        this.log('WebSocket connection closed normally', 'info');
                    }
                };

                this.ws.onerror = (error) => {
                    this.isConnected = false;
                    this.notifyStatusChange(false, 'Connection error');
                    
                    // Provide more detailed error information for debugging
                    let errorMsg = 'WebSocket connection failed';
                    if (error.target && error.target.readyState !== undefined) {
                        switch (error.target.readyState) {
                            case WebSocket.CONNECTING:
                                errorMsg += ' - Connection in progress';
                                break;
                            case WebSocket.OPEN:
                                errorMsg += ' - Connection was open';
                                break;
                            case WebSocket.CLOSING:
                                errorMsg += ' - Connection closing';
                                break;
                            case WebSocket.CLOSED:
                                errorMsg += ' - Connection closed';
                                break;
                        }
                    }
                    
                    // Add browser-specific debugging info
                    const userAgent = navigator.userAgent;
                    if (userAgent.includes('Chrome') && !userAgent.includes('Edge')) {
                        errorMsg += ' (Chrome detected - ensure server supports CORS)';
                    } else if (userAgent.includes('Edg')) {
                        errorMsg += ' (Edge detected - check security settings)';
                    }
                    
                    this.log(errorMsg, 'error');
                    
                    if (!this.isConnected) {
                        reject(new Error(errorMsg));
                    }
                };

                this.ws.onmessage = (event) => {
                    this.handleMessage(event.data);
                };

                // Connection timeout with more detailed message
                const connectionTimeout = setTimeout(() => {
                    if (!this.isConnected) {
                        this.ws.close();
                        const currentUrl = new URL(this.serverUrl);
                        const port = currentUrl.port || 80;
                        reject(new Error(
                            `Connection timeout after 5 seconds.\n\n` +
                            `Troubleshooting:\n` +
                            `• Make sure MCP server is running on port ${port}\n` +
                            `• Check if your browser blocks WebSocket connections\n` +
                            `• Try Firefox if Chrome/Edge don't work\n` +
                            `• Verify the server URL: ${this.serverUrl}`
                        ));
                    }
                }, 5000);

            } catch (error) {
                reject(error);
            }
        });
    }

    async initializeMCP() {
        // Send MCP initialization message
        const initMessage = {
            jsonrpc: '2.0',
            id: ++this.messageId,
            method: 'initialize',
            params: {
                protocolVersion: '2024-11-05',
                capabilities: {
                    tools: {}
                },
                clientInfo: {
                    name: 'SRRD-Builder Frontend Client',
                    version: '1.0.0'
                }
            }
        };

        try {
            const response = await this.sendMessage(initMessage);
            this.log('MCP protocol initialized', 'success');
            return response; // Return the response so the frontend can access serverInfo
        } catch (error) {
            this.log(`MCP initialization failed: ${error.message}`, 'error');
            throw error;
        }
    }

    async attemptReconnect() {
        this.reconnectAttempts++;
        this.log(`Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}...`, 'info');
        
        setTimeout(() => {
            this.connect().catch(error => {
                this.log(`Reconnection failed: ${error.message}`, 'error');
            });
        }, 2000 * this.reconnectAttempts);
    }

    disconnect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.log('Closing WebSocket connection...', 'info');
            this.ws.close(1000, 'Client disconnect');
        }
        this.ws = null;
        this.isConnected = false;
        this.pendingRequests.clear(); // Clear any pending requests
        this.notifyStatusChange(false, 'Disconnected');
    }

    async sendMessage(message) {
        return new Promise((resolve, reject) => {
            if (!this.isConnected || !this.ws) {
                reject(new Error('Not connected to server'));
                return;
            }

            const messageId = message.id;
            this.pendingRequests.set(messageId, { resolve, reject, timestamp: Date.now() });
            
            try {
                this.ws.send(JSON.stringify(message));
                
                // Request timeout
                setTimeout(() => {
                    if (this.pendingRequests.has(messageId)) {
                        this.pendingRequests.delete(messageId);
                        reject(new Error('Request timeout'));
                    }
                }, 30000);
                
            } catch (error) {
                this.pendingRequests.delete(messageId);
                reject(error);
            }
        });
    }

    async callTool(toolName, parameters = {}) {
        if (!this.isConnected) {
            throw new Error('Not connected to server');
        }

        const message = {
            jsonrpc: '2.0',
            id: ++this.messageId,
            method: 'tools/call',
            params: {
                name: toolName,
                arguments: parameters
            }
        };

        try {
            this.log(`Calling tool: ${toolName}`, 'info');
            const result = await this.sendMessage(message);
            this.log(`Tool ${toolName} completed successfully`, 'success');
            return result;
        } catch (error) {
            this.log(`Tool ${toolName} failed: ${error.message}`, 'error');
            throw error;
        }
    }

    async listTools() {
        if (!this.isConnected) {
            throw new Error('Not connected to server');
        }

        const message = {
            jsonrpc: '2.0',
            id: ++this.messageId,
            method: 'tools/list'
        };

        try {
            const result = await this.sendMessage(message);
            this.log(`Listed ${result.tools ? result.tools.length : 0} available tools`, 'info');
            return result;
        } catch (error) {
            this.log(`Failed to list tools: ${error.message}`, 'error');
            throw error;
        }
    }

    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            
            if (message.id && this.pendingRequests.has(message.id)) {
                const request = this.pendingRequests.get(message.id);
                this.pendingRequests.delete(message.id);
                
                if (message.error) {
                    request.reject(new Error(message.error.message || 'Unknown error'));
                } else {
                    request.resolve(message.result);
                }
            } else {
                // Handle notifications or other messages
                if (message.method) {
                    this.log(`Received notification: ${message.method}`, 'info');
                }
            }
            
            if (this.onMessage) {
                this.onMessage(message);
            }
            
        } catch (error) {
            this.log(`Failed to parse message: ${error.message}`, 'error');
        }
    }

    notifyStatusChange(connected, message) {
        if (this.onStatusChange) {
            this.onStatusChange(connected, message);
        }
    }

    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
        const logMessage = `[${timestamp}] ${prefix} ${message}`;
        
        console.log(logMessage);
        
        // Also send to UI if callback is set
        if (this.onMessage) {
            // This will be handled by the UI
        }
    }

    getConnectionStatus() {
        return {
            connected: this.isConnected,
            serverUrl: this.serverUrl,
            pendingRequests: this.pendingRequests.size,
            reconnectAttempts: this.reconnectAttempts
        };
    }

    // Ping the server to check connectivity
    async ping() {
        if (!this.isConnected) {
            throw new Error('Not connected to server');
        }

        const message = {
            jsonrpc: '2.0',
            id: ++this.messageId,
            method: 'ping'
        };

        try {
            await this.sendMessage(message);
            return true;
        } catch (error) {
            return false;
        }
    }
}

// Export for use in the main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MCPClient;
} else {
    window.MCPClient = MCPClient;
}
