# ==========================================================
# ---------- SYSTEM CONTROL MODULE ----------
# ==========================================================
import psutil
import os
import platform
import subprocess
import sys

# ==========================================================
# ---------- BATTERY INFORMATION ----------
# ==========================================================
def get_battery_status():
    """Get battery status and percentage"""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return "No battery detected. System is running on AC power."
        
        percent = battery.percent
        plugged = battery.plugged
        
        if plugged:
            status = f"Battery is at {percent}% and charging."
        else:
            time_left = battery.secsleft
            if time_left != psutil.POWER_TIME_UNLIMITED:
                hours = time_left // 3600
                minutes = (time_left % 3600) // 60
                status = f"Battery is at {percent}%. Approximately {hours} hours and {minutes} minutes remaining."
            else:
                status = f"Battery is at {percent}%."
        
        return status
    except Exception as e:
        return f"Error getting battery status: {e}"

# ==========================================================
# ---------- CPU & RAM USAGE ----------
# ==========================================================
def get_cpu_usage():
    """Get CPU usage percentage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=True)
        return f"CPU usage is {cpu_percent}% across {cpu_count} cores."
    except Exception as e:
        return f"Error getting CPU usage: {e}"

def get_ram_usage():
    """Get RAM usage information"""
    try:
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        used_gb = memory.used / (1024**3)
        available_gb = memory.available / (1024**3)
        percent = memory.percent
        
        return f"RAM usage is {percent}%. Using {used_gb:.2f} GB out of {total_gb:.2f} GB. {available_gb:.2f} GB available."
    except Exception as e:
        return f"Error getting RAM usage: {e}"

def get_system_stats():
    """Get combined CPU and RAM stats"""
    cpu_info = get_cpu_usage()
    ram_info = get_ram_usage()
    return f"{cpu_info} {ram_info}"

# ==========================================================
# ---------- DISK SPACE INFORMATION ----------
# ==========================================================
def get_disk_space():
    """Get disk space information for all drives"""
    try:
        partitions = psutil.disk_partitions()
        disk_info = []
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                free_gb = usage.free / (1024**3)
                percent = usage.percent
                
                info = f"{partition.device} has {free_gb:.2f} GB free out of {total_gb:.2f} GB. {percent}% used."
                disk_info.append(info)
            except:
                continue
        
        return " ".join(disk_info) if disk_info else "No disk information available."
    except Exception as e:
        return f"Error getting disk space: {e}"

# ==========================================================
# ---------- SYSTEM POWER MANAGEMENT ----------
# ==========================================================
def shutdown_system():
    """Shutdown the system"""
    try:
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown -h now")
        return "Shutting down system now."
    except Exception as e:
        return f"Error shutting down: {e}"

def restart_system():
    """Restart the system"""
    try:
        if platform.system() == "Windows":
            os.system("shutdown /r /t 1")
        else:
            os.system("shutdown -r now")
        return "Restarting system now."
    except Exception as e:
        return f"Error restarting: {e}"

def sleep_system():
    """Put system to sleep"""
    try:
        if platform.system() == "Windows":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            os.system("systemctl suspend")
        return "Putting system to sleep."
    except Exception as e:
        return f"Error putting system to sleep: {e}"

