/**
 * MCP WebSocket Client for Frontend Testing
 * Handles real WebSocket connections to the MCP server with proper protocol
 */

class MCPClient {
    constructor(serverUrl = 'ws://localhost:8083') {
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
                
                // Create WebSocket with proper protocol
                this.ws = new WebSocket(this.serverUrl, ['mcp']);
                
                this.ws.onopen = () => {
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.notifyStatusChange(true, 'Connected to MCP Server');
                    this.log('WebSocket connection established', 'success');
                    
                    // Send MCP initialization
                    this.initializeMCP().then(() => {
                        resolve();
                    }).catch(reject);
                };

                this.ws.onclose = (event) => {
                    this.isConnected = false;
                    this.notifyStatusChange(false, `Connection closed (${event.code})`);
                    this.log(`WebSocket connection closed: ${event.code} - ${event.reason}`, 'info');
                    
                    // Attempt reconnection if not intentional
                    if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.attemptReconnect();
                    }
                };

                this.ws.onerror = (error) => {
                    this.isConnected = false;
                    this.notifyStatusChange(false, 'Connection error');
                    this.log(`WebSocket error: ${error}`, 'error');
                    
                    if (!this.isConnected) {
                        reject(new Error('Failed to connect to MCP server'));
                    }
                };

                this.ws.onmessage = (event) => {
                    this.handleMessage(event.data);
                };

                // Connection timeout
                setTimeout(() => {
                    if (!this.isConnected) {
                        this.ws.close();
                        reject(new Error('Connection timeout - make sure MCP server is running on localhost:8083'));
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
            await this.sendMessage(initMessage);
            this.log('MCP protocol initialized', 'success');
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
        if (this.ws) {
            this.ws.close(1000, 'Client disconnect');
            this.ws = null;
        }
        this.isConnected = false;
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
