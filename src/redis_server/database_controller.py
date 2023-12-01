import subprocess

def start_redis(conf_path):
    cmd = f'redis-server {conf_path}'
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    print("Redis Start:", result.stdout)
    print("Redis Start Error:", result.stderr)

def stop_redis():
    cmd = 'redis-cli shutdown'
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    print("Redis Shutdown:", result.stdout)
    print("Redis Shutdown Error:", result.stderr)