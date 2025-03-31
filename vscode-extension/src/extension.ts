import * as vscode from 'vscode';
import { io, Socket } from 'socket.io-client';
import axios from 'axios';
import { SyncProvider } from './providers/SyncProvider';
import { AgentProvider } from './providers/AgentProvider';
import { ProjectExplorerProvider } from './providers/ProjectExplorerProvider';

let socket: Socket;

export async function activate(context: vscode.ExtensionContext) {
    const syncProvider = new SyncProvider();
    const agentProvider = new AgentProvider();
    const projectExplorerProvider = new ProjectExplorerProvider();

    // Register views
    vscode.window.registerTreeDataProvider('ade.projectExplorer', projectExplorerProvider);
    vscode.window.registerTreeDataProvider('ade.agents', agentProvider);
    vscode.window.registerTreeDataProvider('ade.sync', syncProvider);

    // Connect to ADE Platform
    const connectCommand = vscode.commands.registerCommand('ade.connect', async () => {
        try {
            const config = vscode.workspace.getConfiguration('ade');
            const serverUrl = config.get<string>('serverUrl');

            socket = io(serverUrl!, {
                reconnection: true,
                reconnectionDelay: 1000,
            });

            socket.on('connect', () => {
                vscode.window.showInformationMessage('Connected to ADE Platform');
                syncProvider.setConnected(true);
            });

            socket.on('disconnect', () => {
                vscode.window.showWarningMessage('Disconnected from ADE Platform');
                syncProvider.setConnected(false);
            });

            // File change events
            socket.on('file:change', async (data: { path: string; content: string }) => {
                const uri = vscode.Uri.file(data.path);
                const edit = new vscode.WorkspaceEdit();
                edit.createFile(uri, { overwrite: true });
                edit.insert(uri, new vscode.Position(0, 0), data.content);
                await vscode.workspace.applyEdit(edit);
            });

            // Agent events
            socket.on('agent:start', (data) => {
                agentProvider.addAgent(data);
            });

            socket.on('agent:stop', (data) => {
                agentProvider.removeAgent(data.id);
            });

        } catch (error) {
            vscode.window.showErrorMessage('Failed to connect to ADE Platform');
        }
    });

    // Sync command
    const syncCommand = vscode.commands.registerCommand('ade.sync', async () => {
        try {
            const config = vscode.workspace.getConfiguration('ade');
            const serverUrl = config.get<string>('serverUrl');

            // Get all workspace files
            const files = await vscode.workspace.findFiles('**/*', '**/node_modules/**');
            
            for (const file of files) {
                const document = await vscode.workspace.openTextDocument(file);
                const content = document.getText();
                const relativePath = vscode.workspace.asRelativePath(file);

                await axios.post(`${serverUrl}/api/sync`, {
                    path: relativePath,
                    content: content,
                    timestamp: Date.now()
                });
            }

            vscode.window.showInformationMessage('Synchronized with ADE Platform');
            syncProvider.updateLastSync();
        } catch (error) {
            vscode.window.showErrorMessage('Sync failed');
        }
    });

    // Start AI Agent command
    const startAgentCommand = vscode.commands.registerCommand('ade.startAgent', async () => {
        const agents = ['Code Generator', 'Refactoring', 'Documentation', 'Testing'];
        const selected = await vscode.window.showQuickPick(agents, {
            placeHolder: 'Select an AI agent to start'
        });

        if (selected) {
            socket.emit('agent:request', { type: selected });
            vscode.window.showInformationMessage(`Started ${selected} agent`);
        }
    });

    // File system watcher for auto-sync
    const watcher = vscode.workspace.createFileSystemWatcher('**/*');
    const config = vscode.workspace.getConfiguration('ade');
    
    if (config.get<boolean>('autoSync')) {
        watcher.onDidChange(async (uri) => {
            if (socket?.connected) {
                const document = await vscode.workspace.openTextDocument(uri);
                socket.emit('file:change', {
                    path: vscode.workspace.asRelativePath(uri),
                    content: document.getText(),
                    timestamp: Date.now()
                });
            }
        });
    }

    context.subscriptions.push(
        connectCommand,
        syncCommand,
        startAgentCommand,
        watcher
    );
}

export function deactivate() {
    if (socket) {
        socket.disconnect();
    }
}
