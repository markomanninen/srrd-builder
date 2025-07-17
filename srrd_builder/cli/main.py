#!/usr/bin/env python3
"""
SRRD-Builder CLI Main Entry Point
"""

import sys
import argparse
from pathlib import Path

def create_parser():
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        prog='srrd',
        description='Scientific Research Requirement Document Builder'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 0.1.0'
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )
    
    # srrd init command
    init_parser = subparsers.add_parser(
        'init',
        help='Initialize SRRD in current Git repository'
    )
    init_parser.add_argument(
        '--force',
        action='store_true',
        help='Force initialization even if .srrd directory exists'
    )
    
    # srrd serve command with subcommands
    serve_parser = subparsers.add_parser(
        'serve',
        help='Manage SRRD MCP server'
    )
    
    # Add serve subcommands
    serve_subparsers = serve_parser.add_subparsers(
        dest='serve_action',
        help='Server actions'
    )
    
    # serve start subcommand
    start_parser = serve_subparsers.add_parser(
        'start',
        help='Start MCP server'
    )
    start_parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Server port (default: 8080)'
    )
    start_parser.add_argument(
        '--host',
        default='localhost',
        help='Server host (default: localhost)'
    )
    
    # serve stop subcommand
    stop_parser = serve_subparsers.add_parser(
        'stop',
        help='Stop MCP server'
    )
    
    # serve restart subcommand
    restart_parser = serve_subparsers.add_parser(
        'restart',
        help='Restart MCP server'
    )
    restart_parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Server port (default: 8080)'
    )
    restart_parser.add_argument(
        '--host',
        default='localhost',
        help='Server host (default: localhost)'
    )
    
    # Set default values for serve command when no subcommand is given
    serve_parser.set_defaults(port=8080, host='localhost')
    
    # srrd generate command
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate research documents'
    )
    generate_parser.add_argument(
        'doc_type',
        choices=['proposal', 'manuscript', 'latex'],
        help='Type of document to generate'
    )
    generate_parser.add_argument(
        '--title',
        required=True,
        help='Document title'
    )
    generate_parser.add_argument(
        '--output',
        default='./documents',
        help='Output directory (default: ./documents)'
    )
    
    # srrd status command
    status_parser = subparsers.add_parser(
        'status',
        help='Check SRRD server and project status'
    )
    
    # srrd configure command
    configure_parser = subparsers.add_parser(
        'configure',
        help='Configure MCP server for IDEs (Claude Desktop, VS Code)'
    )
    configure_parser.add_argument(
        '--claude',
        action='store_true',
        help='Configure Claude Desktop'
    )
    configure_parser.add_argument(
        '--vscode',
        action='store_true',
        help='Configure VS Code'
    )
    configure_parser.add_argument(
        '--all',
        action='store_true',
        help='Configure all supported IDEs'
    )
    configure_parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing configuration'
    )
    configure_parser.add_argument(
        '--status',
        dest='show_status',
        action='store_true',
        help='Show current configuration status'
    )
    
    return parser

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Import command handlers
    if args.command == 'init':
        from .commands.init import handle_init
        return handle_init(args)
    elif args.command == 'serve':
        from .commands.serve import handle_serve
        return handle_serve(args)
    elif args.command == 'generate':
        from .commands.generate import handle_generate
        return handle_generate(args)
    elif args.command == 'status':
        from .commands.status import handle_status
        return handle_status(args)
    elif args.command == 'configure':
        from .commands.configure import handle_configure
        return handle_configure(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
