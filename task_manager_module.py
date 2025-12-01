import json
import os
from datetime import datetime, timedelta

class TaskManager:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    self.tasks = json.load(f)
            else:
                self.tasks = []
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.tasks, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            return False
    
    def add_task(self, title, priority="medium", due_date=None, category="general"):
        """Add a new task"""
        if not title or title.strip() == "":
            return False, "Task title cannot be empty"
        
        priority = priority.lower()
        if priority not in ["low", "medium", "high"]:
            priority = "medium"
        
        task = {
            "id": len(self.tasks) + 1,
            "title": title.strip(),
            "priority": priority,
            "due_date": due_date,
            "category": category.strip().lower(),
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.tasks.append(task)
        self.save_tasks()
        return True, f"Task '{title}' added successfully with {priority} priority"
    
    def remove_task(self, task_id=None, title=None):
        """Remove a task by ID or title"""
        initial_count = len(self.tasks)
        
        if task_id is not None:
            self.tasks = [task for task in self.tasks if task["id"] != task_id]
        elif title is not None:
            title_lower = title.lower()
            self.tasks = [task for task in self.tasks if title_lower not in task["title"].lower()]
        else:
            return False, "Please provide task ID or title"
        
        if len(self.tasks) < initial_count:
            self.save_tasks()
            return True, "Task removed successfully"
        else:
            return False, "Task not found"
    
    def complete_task(self, task_id=None, title=None):
        """Mark a task as completed"""
        found = False
        
        if task_id is not None:
            for task in self.tasks:
                if task["id"] == task_id:
                    task["completed"] = True
                    task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    found = True
                    break
        elif title is not None:
            title_lower = title.lower()
            for task in self.tasks:
                if title_lower in task["title"].lower():
                    task["completed"] = True
                    task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    found = True
                    break
        else:
            return False, "Please provide task ID or title"
        
        if found:
            self.save_tasks()
            return True, "Task marked as completed"
        else:
            return False, "Task not found"
    
    def get_all_tasks(self, show_completed=True):
        """Get all tasks"""
        if show_completed:
            return self.tasks
        else:
            return [task for task in self.tasks if not task["completed"]]
    
    def get_tasks_by_priority(self, priority):
        """Get tasks filtered by priority"""
        priority = priority.lower()
        return [task for task in self.tasks if task["priority"] == priority and not task["completed"]]
    
    def get_tasks_by_category(self, category):
        """Get tasks filtered by category"""
        category = category.lower()
        return [task for task in self.tasks if task["category"] == category and not task["completed"]]
    
    def get_due_tasks(self):
        """Get tasks that are due soon (within 24 hours)"""
        due_tasks = []
        now = datetime.now()
        
        for task in self.tasks:
            if task["completed"]:
                continue
            
            if task["due_date"]:
                try:
                    due_date = datetime.strptime(task["due_date"], "%Y-%m-%d %H:%M:%S")
                    time_diff = due_date - now
                    
                    if timedelta(0) <= time_diff <= timedelta(days=1):
                        due_tasks.append(task)
                except Exception:
                    pass
        
        return due_tasks
    
    def get_overdue_tasks(self):
        """Get tasks that are overdue"""
        overdue_tasks = []
        now = datetime.now()
        
        for task in self.tasks:
            if task["completed"]:
                continue
            
            if task["due_date"]:
                try:
                    due_date = datetime.strptime(task["due_date"], "%Y-%m-%d %H:%M:%S")
                    if due_date < now:
                        overdue_tasks.append(task)
                except Exception:
                    pass
        
        return overdue_tasks
    
    def format_task_list(self, tasks):
        """Format tasks for display"""
        if not tasks:
            return "No tasks found"
        
        output = "\n" + "="*60 + "\n"
        for task in tasks:
            status = "✓" if task["completed"] else "○"
            priority_symbol = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task["priority"], "○")
            
            output += f"{status} [{task['id']}] {priority_symbol} {task['title']}\n"
            output += f"   Priority: {task['priority'].upper()} | Category: {task['category']}\n"
            
            if task["due_date"]:
                output += f"   Due: {task['due_date']}\n"
            
            if task["completed"]:
                output += f"   Completed: {task.get('completed_at', 'Unknown')}\n"
            
            output += "-"*60 + "\n"
        
        return output


def handle_task_commands(query, task_manager, speak_func):
    """Handle all task-related commands"""
    query = query.lower().strip()
    
    # Add task
    if "add task" in query or "create task" in query or "new task" in query:
        speak_func("What is the task title?")
        title = input("Task title: ").strip()
        
        if not title:
            speak_func("Task title cannot be empty")
            return
        
        speak_func("What is the priority? Say low, medium, or high")
        priority = input("Priority (low/medium/high): ").strip().lower()
        if priority not in ["low", "medium", "high"]:
            priority = "medium"
        
        speak_func("Do you want to set a due date? Say yes or no")
        due_choice = input("Set due date? (yes/no): ").strip().lower()
        due_date = None
        
        if due_choice == "yes" or "yes" in due_choice:
            speak_func("Enter due date in format: YYYY-MM-DD HH:MM:SS or just YYYY-MM-DD")
            due_input = input("Due date: ").strip()
            
            if due_input:
                try:
                    if len(due_input) == 10:
                        due_date = due_input + " 23:59:59"
                    else:
                        due_date = due_input
                    datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    speak_func("Invalid date format. Setting no due date")
                    due_date = None
        
        speak_func("What category? For example: work, personal, shopping, or general")
        category = input("Category: ").strip()
        if not category:
            category = "general"
        
        success, message = task_manager.add_task(title, priority, due_date, category)
        speak_func(message)
        return
    
    # Remove task
    elif "remove task" in query or "delete task" in query:
        tasks = task_manager.get_all_tasks(show_completed=False)
        if not tasks:
            speak_func("No tasks to remove")
            return
        
        print(task_manager.format_task_list(tasks))
        speak_func("Enter task ID or title to remove")
        identifier = input("Task ID or title: ").strip()
        
        if identifier.isdigit():
            success, message = task_manager.remove_task(task_id=int(identifier))
        else:
            success, message = task_manager.remove_task(title=identifier)
        
        speak_func(message)
        return
    
    # Complete task
    elif "complete task" in query or "finish task" in query or "done task" in query:
        tasks = task_manager.get_all_tasks(show_completed=False)
        if not tasks:
            speak_func("No tasks to complete")
            return
        
        print(task_manager.format_task_list(tasks))
        speak_func("Enter task ID or title to mark as completed")
        identifier = input("Task ID or title: ").strip()
        
        if identifier.isdigit():
            success, message = task_manager.complete_task(task_id=int(identifier))
        else:
            success, message = task_manager.complete_task(title=identifier)
        
        speak_func(message)
        return
    
    # Show all tasks
    elif "show tasks" in query or "list tasks" in query or "all tasks" in query or "view tasks" in query:
        speak_func("Do you want to see completed tasks too? Say yes or no")
        choice = input("Show completed? (yes/no): ").strip().lower()
        show_completed = choice == "yes" or "yes" in choice
        
        tasks = task_manager.get_all_tasks(show_completed=show_completed)
        formatted = task_manager.format_task_list(tasks)
        print(formatted)
        speak_func(f"Found {len(tasks)} tasks")
        return
    
    # Show tasks by priority
    elif "high priority" in query or "medium priority" in query or "low priority" in query:
        if "high" in query:
            priority = "high"
        elif "medium" in query:
            priority = "medium"
        else:
            priority = "low"
        
        tasks = task_manager.get_tasks_by_priority(priority)
        formatted = task_manager.format_task_list(tasks)
        print(formatted)
        speak_func(f"Found {len(tasks)} {priority} priority tasks")
        return
    
    # Show tasks by category
    elif "category" in query:
        speak_func("Which category? For example: work, personal, shopping")
        category = input("Category: ").strip()
        
        if category:
            tasks = task_manager.get_tasks_by_category(category)
            formatted = task_manager.format_task_list(tasks)
            print(formatted)
            speak_func(f"Found {len(tasks)} tasks in {category} category")
        return
    
    # Check due tasks
    elif "due tasks" in query or "due soon" in query or "upcoming tasks" in query:
        tasks = task_manager.get_due_tasks()
        formatted = task_manager.format_task_list(tasks)
        print(formatted)
        speak_func(f"Found {len(tasks)} tasks due within 24 hours")
        return
    
    # Check overdue tasks
    elif "overdue" in query or "late tasks" in query:
        tasks = task_manager.get_overdue_tasks()
        formatted = task_manager.format_task_list(tasks)
        print(formatted)
        speak_func(f"Found {len(tasks)} overdue tasks")
        return
    
    else:
        speak_func("I didn't understand that task command. You can say: add task, remove task, complete task, show tasks, high priority tasks, due tasks, or overdue tasks")
        return
