#!/usr/bin/env python3
import os
import yaml
import sys
from datetime import datetime
import inquirer
from rich.console import Console
from rich.table import Table
from rich import box

CONFIG_FILE = "config.yaml"

# Initialize rich console
console = Console()

# ------------------ UTILITY FUNCTIONS ------------------

def load_config():
    """Load YAML configuration file"""
    try:
        with open(CONFIG_FILE, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Configuration file {CONFIG_FILE} not found!", style="red")
        sys.exit(1)

def save_config(data):
    """Save configuration to YAML file"""
    with open(CONFIG_FILE, 'w') as file:
        yaml.dump(data, file, sort_keys=False)

def display_header(title):
    """Display a styled header"""
    console.print(f"\n[bold bright_cyan]{'=' * 50}[/bold bright_cyan]")
    console.print(f"[bold bright_yellow]{title.center(50)}[/bold bright_yellow]")
    console.print(f"[bold bright_cyan]{'=' * 50}[/bold bright_cyan]\n")

def validate_date(_, date):
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD"

# ------------------ PROJECT MANAGEMENT ------------------

def manage_projects():
    """Main menu for project management"""
    while True:
        config = load_config()
        projects = config.get('projects', [])
        
        display_header("PROJECT MANAGEMENT")
        
        choices = [
            ('List all projects', 'list'),
            ('Add new project', 'add'),
            ('Edit existing project', 'edit'),
            ('Remove project', 'remove'),
            ('Return to main menu', 'back')
        ]
        
        questions = [
            inquirer.List('action',
                          message="Select operation",
                          choices=choices)
        ]
        action = inquirer.prompt(questions)['action']
        
        if action == 'back':
            return
        elif action == 'list':
            list_projects(projects)
        elif action == 'add':
            add_project(config)
        elif action == 'edit':
            edit_project(config, projects)
        elif action == 'remove':
            remove_project(config, projects)

def list_projects(projects):
    """Display projects in a formatted table"""
    if not projects:
        console.print("[italic]No projects found[/italic]")
        return

    table = Table(title="\nPROJECTS", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Start Date", style="green")
    table.add_column("End Date", style="yellow")
    table.add_column("Freeze Date", style="bright_red")
    table.add_column("CommonConfig", justify="center")

    for project in projects:
        cc_flag = "✓" if project.get('commonconfig') == "true" else ""
        table.add_row(
            project['name'],
            project.get('start_date', 'N/A'),
            project.get('end_date', 'N/A'),
            project.get('freeze_date', 'N/A'),
            cc_flag
        )
    
    console.print(table)

def add_project(config):
    """Add a new project"""
    display_header("ADD NEW PROJECT")
    
    questions = [
        inquirer.Text('name', message="Project name"),
        inquirer.Text('start_date', message="Start date (YYYY-MM-DD)", validate=validate_date),
        inquirer.Text('end_date', message="End date (YYYY-MM-DD)", validate=validate_date),
        inquirer.Text('freeze_date', message="Freeze date (YYYY-MM-DD)", validate=validate_date),
        inquirer.Confirm('commonconfig', message="Is this a CommonConfig project?", default=False),
        inquirer.Confirm('confirm', message="Confirm creation?", default=True)
    ]
    
    answers = inquirer.prompt(questions)
    
    if answers['confirm']:
        new_project = {
            'name': answers['name'],
            'start_date': answers['start_date'],
            'end_date': answers['end_date'],
            'freeze_date': answers['freeze_date'],
            'commonconfig': "true" if answers['commonconfig'] else "false"
        }
        
        config['projects'].append(new_project)
        save_config(config)
        console.print(f"[bold green]✓ Project '{answers['name']}' created successfully![/bold green]")
    else:
        console.print("[yellow]Project creation canceled[/yellow]")

def edit_project(config, projects):
    """Edit an existing project"""
    if not projects:
        console.print("[italic yellow]No projects to edit[/italic yellow]")
        return
        
    project_choices = [(f"{p['name']} (Start: {p.get('start_date', 'N/A')})", p) for p in projects]
    
    questions = [
        inquirer.List('project', 
                      message="Select project to edit",
                      choices=project_choices)
    ]
    selected = inquirer.prompt(questions)['project']
    
    display_header(f"EDIT PROJECT: {selected['name']}")
    
    questions = [
        inquirer.Text('name', message="Project name", default=selected['name']),
        inquirer.Text('start_date', message="Start date", 
                      default=selected.get('start_date', ''), validate=validate_date),
        inquirer.Text('end_date', message="End date", 
                      default=selected.get('end_date', ''), validate=validate_date),
        inquirer.Text('freeze_date', message="Freeze date", 
                      default=selected.get('freeze_date', ''), validate=validate_date),
        inquirer.Confirm('commonconfig', 
                         message="Is this a CommonConfig project?", 
                         default=selected.get('commonconfig', 'false') == "true"),
        inquirer.Confirm('confirm', message="Save changes?", default=True)
    ]
    
    answers = inquirer.prompt(questions)
    
    if answers['confirm']:
        # Update project in config
        for project in config['projects']:
            if project['name'] == selected['name']:
                project.update({
                    'name': answers['name'],
                    'start_date': answers['start_date'],
                    'end_date': answers['end_date'],
                    'freeze_date': answers['freeze_date'],
                    'commonconfig': "true" if answers['commonconfig'] else "false"
                })
                break
        
        save_config(config)
        console.print(f"[bold green]✓ Project '{answers['name']}' updated![/bold green]")
    else:
        console.print("[yellow]Project update canceled[/yellow]")

def remove_project(config, projects):
    """Remove a project"""
    if not projects:
        console.print("[italic yellow]No projects to remove[/italic yellow]")
        return
        
    project_choices = [(p['name'], p) for p in projects]
    
    questions = [
        inquirer.Checkbox('projects', 
                          message="Select projects to remove",
                          choices=project_choices),
        inquirer.Confirm('confirm', message="Confirm deletion?", default=False)
    ]
    
    answers = inquirer.prompt(questions)
    
    if answers['confirm'] and answers['projects']:
        # Create list of names to remove
        to_remove = [p['name'] for p in answers['projects']]
        
        # Filter out removed projects
        config['projects'] = [p for p in config['projects'] if p['name'] not in to_remove]
        
        save_config(config)
        console.print(f"[bold green]✓ Removed {len(to_remove)} project(s)[/bold green]")
    else:
        console.print("[yellow]Project removal canceled[/yellow]")

# ------------------ CHANGE REQUEST MANAGEMENT ------------------

def manage_change_requests():
    """Main menu for change request management"""
    while True:
        config = load_config()
        requests = config.get('change_requests', [])
        filters = config.get('project_filters', [])
        
        display_header("CHANGE REQUEST MANAGEMENT")
        
        choices = [
            ('List all requests', 'list'),
            ('Filter requests', 'filter'),
            ('Add new request', 'add'),
            ('Edit existing request', 'edit'),
            ('Change request state', 'state'),
            ('Remove request', 'remove'),
            ('Return to main menu', 'back')
        ]
        
        questions = [
            inquirer.List('action',
                          message="Select operation",
                          choices=choices)
        ]
        action = inquirer.prompt(questions)['action']
        
        if action == 'back':
            return
        elif action == 'list':
            list_requests(requests)
        elif action == 'filter':
            filter_requests(requests, filters)
        elif action == 'add':
            add_request(config, filters)
        elif action == 'edit':
            edit_request(config, requests, filters)
        elif action == 'state':
            change_request_state(config, requests)
        elif action == 'remove':
            remove_request(config, requests)

def list_requests(requests, title="ALL CHANGE REQUESTS"):
    """Display change requests in a formatted table"""
    if not requests:
        console.print("[italic]No change requests found[/italic]")
        return

    table = Table(title=f"\n{title}", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("Project", style="green")
    table.add_column("State", style="yellow")
    table.add_column("Created", style="bright_blue")
    table.add_column("Body Preview", style="white")

    for req in requests:
        # Truncate body for display
        body_preview = req['body'][:30] + '...' if len(req['body']) > 30 else req['body']
        
        # State styling with new fulfilled_prio state
        state_style = {
            'open': 'bright_red',
            'in_progress': 'bright_yellow',
            'integrated': 'bright_green',
            'fulfilled_prio': 'bright_magenta'  # NEW STATE STYLE
        }.get(req['state'], 'white')
        
        # Display text for new state
        display_state = "fulfilled (prio)" if req['state'] == 'fulfilled_prio' else req['state']
        
        table.add_row(
            req['title'],
            req.get('project', 'N/A'),
            f'[{state_style}]{display_state}[/{state_style}]',
            req.get('created', 'N/A'),
            body_preview
        )
    
    console.print(table)

def filter_requests(requests, filters):
    """Filter requests by project and state"""
    display_header("FILTER REQUESTS")
    
    # Add new state to choices
    state_choices = ['open', 'in_progress', 'integrated', 'fulfilled_prio', 'all']
    filter_choices = filters + ['all']
    
    questions = [
        inquirer.List('project', 
                      message="Filter by project",
                      choices=filter_choices),
        inquirer.List('state', 
                      message="Filter by state",
                      choices=state_choices)
    ]
    
    filters = inquirer.prompt(questions)
    filtered = requests.copy()
    
    # Apply project filter
    if filters['project'] != 'all':
        filtered = [r for r in filtered if r.get('project') == filters['project']]
    
    # Apply state filter
    if filters['state'] != 'all':
        filtered = [r for r in filtered if r.get('state') == filters['state']]
    
    # Format title with state display name
    state_display = {
        'fulfilled_prio': 'fulfilled (prio)',
        'in_progress': 'in progress'
    }.get(filters['state'], filters['state'])
    
    title = f"REQUESTS: {filters['project'].upper()} | {state_display.upper()}"
    list_requests(filtered, title)

def add_request(config, filters):
    """Add a new change request"""
    display_header("ADD CHANGE REQUEST")
    
    # Add new state to choices
    state_choices = ['open', 'in_progress', 'integrated', 'fulfilled_prio']
    
    questions = [
        inquirer.Text('title', message="Request title"),
        inquirer.Text('body', message="Description"),
        inquirer.List('project', 
                      message="Project",
                      choices=filters),
        inquirer.List('state', 
                      message="Initial state",
                      choices=state_choices),
        inquirer.Text('created', 
                      message="Created date (YYYY-MM-DD)", 
                      default=datetime.now().strftime('%Y-%m-%d'),
                      validate=validate_date),
        inquirer.Confirm('confirm', message="Confirm creation?", default=True)
    ]
    
    answers = inquirer.prompt(questions)
    
    if answers['confirm']:
        new_request = {
            'title': answers['title'],
            'body': answers['body'],
            'project': answers['project'],
            'state': answers['state'],
            'created': answers['created']
        }
        
        config['change_requests'].append(new_request)
        save_config(config)
        console.print(f"[bold green]✓ Request '{answers['title']}' created![/bold green]")
    else:
        console.print("[yellow]Request creation canceled[/yellow]")

def edit_request(config, requests, filters):
    """Edit an existing change request"""
    if not requests:
        console.print("[italic yellow]No change requests to edit[/italic yellow]")
        return
        
    request_choices = [(f"{r['title']} ({r['project']})", r) for r in requests]
    
    questions = [
        inquirer.List('request', 
                      message="Select request to edit",
                      choices=request_choices)
    ]
    selected = inquirer.prompt(questions)['request']
    
    display_header(f"EDIT REQUEST: {selected['title']}")
    
    questions = [
        inquirer.Text('title', message="Title", default=selected['title']),
        inquirer.Text('body', message="Description", default=selected['body']),
        inquirer.List('project', 
                      message="Project",
                      choices=filters,
                      default=selected.get('project', '')),
        inquirer.Text('created', 
                      message="Created date", 
                      default=selected.get('created', ''),
                      validate=validate_date),
        inquirer.Confirm('confirm', message="Save changes?", default=True)
    ]
    
    answers = inquirer.prompt(questions)
    
    if answers['confirm']:
        # Update request in config
        for req in config['change_requests']:
            if req['title'] == selected['title'] and req.get('project') == selected.get('project'):
                req.update({
                    'title': answers['title'],
                    'body': answers['body'],
                    'project': answers['project'],
                    'created': answers['created']
                })
                break
        
        save_config(config)
        console.print(f"[bold green]✓ Request '{answers['title']}' updated![/bold green]")
    else:
        console.print("[yellow]Request update canceled[/yellow]")

def change_request_state(config, requests):
    """Change the state of a request"""
    if not requests:
        console.print("[italic yellow]No change requests to modify[/italic yellow]")
        return
        
    request_choices = [(f"{r['title']} ({r['project']} - {r['state']})", r) for r in requests]
    
    # Add new state to choices
    state_choices = ['open', 'in_progress', 'integrated', 'fulfilled_prio']
    
    questions = [
        inquirer.List('request', 
                      message="Select request",
                      choices=request_choices),
        inquirer.List('state', 
                      message="New state",
                      choices=state_choices),
        inquirer.Confirm('confirm', message="Confirm state change?", default=True)
    ]
    
    answers = inquirer.prompt(questions)
    
    if answers['confirm']:
        # Update request state in config
        selected = answers['request']
        for req in config['change_requests']:
            if req['title'] == selected['title'] and req.get('project') == selected.get('project'):
                old_state = req['state']
                req['state'] = answers['state']
                break
        
        save_config(config)
        
        # Display friendly state names
        state_names = {
            'fulfilled_prio': 'fulfilled (in prio version)',
            'in_progress': 'in progress'
        }
        old_display = state_names.get(old_state, old_state)
        new_display = state_names.get(answers['state'], answers['state'])
        
        console.print(f"[bold green]✓ State changed from {old_display} to {new_display}![/bold green]")
    else:
        console.print("[yellow]State change canceled[/yellow]")

def remove_request(config, requests):
    """Remove change requests"""
    if not requests:
        console.print("[italic yellow]No change requests to remove[/italic yellow]")
        return
        
    request_choices = [(f"{r['title']} ({r['project']})", r) for r in requests]
    
    questions = [
        inquirer.Checkbox('requests', 
                          message="Select requests to remove",
                          choices=request_choices),
        inquirer.Confirm('confirm', message="Confirm deletion?", default=False)
    ]
    
    answers = inquirer.prompt(questions)
    
    if answers['confirm'] and answers['requests']:
        # Create list of identifiers for removal
        to_remove = []
        for req in answers['requests']:
            to_remove.append((req['title'], req.get('project')))
        
        # Filter out removed requests
        config['change_requests'] = [
            r for r in config['change_requests'] 
            if (r['title'], r.get('project')) not in to_remove
        ]
        
        save_config(config)
        console.print(f"[bold green]✓ Removed {len(to_remove)} request(s)[/bold green]")
    else:
        console.print("[yellow]Request removal canceled[/yellow]")

# ------------------ MAIN FUNCTION ------------------

def print_welcome():
    """Display welcome message and background text"""
    config = load_config()
    bg_text = config.get('background_text', 'CommonConfig Management System')
    
    console.print(f"\n[bold bright_cyan]{'=' * 60}[/bold bright_cyan]")
    console.print(f"[bold bright_yellow]COMMONCONFIG MANAGEMENT SYSTEM[/bold bright_yellow]".center(60))
    console.print(f"[bold bright_cyan]{'=' * 60}[/bold bright_cyan]")
    console.print(f"\n[italic bright_white]{bg_text}[/italic bright_white]\n")

def main():
    print_welcome()
    
    while True:
        display_header("MAIN MENU")
        
        choices = [
            ('Manage Projects', 'projects'),
            ('Manage Change Requests', 'requests'),
            ('View Full Configuration', 'view'),
            ('Exit', 'exit')
        ]
        
        questions = [
            inquirer.List('action',
                          message="Select operation",
                          choices=choices)
        ]
        action = inquirer.prompt(questions)['action']
        
        if action == 'exit':
            console.print("\n[bold bright_green]Goodbye![/bold bright_green]\n")
            break
        elif action == 'projects':
            manage_projects()
        elif action == 'requests':
            manage_change_requests()
        elif action == 'view':
            config = load_config()
            console.print(config)

if __name__ == "__main__":
    main()
