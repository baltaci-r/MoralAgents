
if [ "$#" -lt 4 ]; then
  echo "Error: Insufficient arguments provided."
  echo "Usage: bash $0 <model_name> <num_agents> <dataset>"
  echo "  <model_name>:         Name of the model to use      (e.g., llama3.3, gpt-4.1)"
  echo "  <num_agents>:         Number of agents              (e.g., 1, 2, 3)"
  echo "  <dataset>:            Dataset to use                (e.g., keshmirian, greene, korner, cni, oxford_utilitarianism_scale)"
  echo "  <task_id>:            Task id                     (e.g., 1)"
  echo "================================================"
  echo "Example: "
  echo "[Single]"
  echo "bash run.sh run.slurm qwen3:32b 1 greene"
  echo "bash run.sh qwen3:32b 1 korner"
  echo "bash run.sh qwen3:32b 1 keshmirian"
  echo "bash run.sh qwen3:32b 1 cni"
  echo "bash run.sh qwen3:32b 1 oxford_utilitarianism_scale"
  echo "[DYAD]"
  echo "bash run.sh qwen3:32b 2 greene"
  echo "bash run.sh qwen3:32b 2 korner"
  echo "bash run.sh qwen3:32b 2 keshmirian"
  echo "bash run.sh qwen3:32b 2 cni"
  echo "bash run.sh qwen3:32b 2 oxford_utilitarianism_scale"
  echo "[TRIAD]"
  echo "bash run.sh qwen3:32b 3 greene"
  echo "bash run.sh qwen3:32b 3 korner"
  echo "bash run.sh qwen3:32b 3 keshmirian"
  echo "bash run.sh qwen3:32b 3 cni"
  echo "bash run.sh qwen3:32b 3 oxford_utilitarianism_scale"
  echo "================================================"
  exit 1
fi

model_name=$1
num_agents=$2
dataset=$3

# Set temperature based on model name
if [[ $model_name == *"gpt"* ]] || [[ $model_name == *"o"* ]]; then
    temperature=0.7 # Use 0.7 for GPT
    n_ctx=32768
elif [[ $model_name == *"qwen3"* ]]; then
    temperature=0.6 # Use 0.6 for qwen3 default in ollama
    n_ctx=32768
elif [[ $model_name == *"gemma"* ]]; then
    temperature=1.0 # Use 1.0 for gemma default in ollama
    n_ctx=32768
else
    temperature=0.8 # Use 0.8 for other models (default in ollama if model has no default temperature)
    n_ctx=32768
fi

echo "Using temperature=$temperature, n_ctx=$n_ctx context length for $model_name"

# Set number of round:
if [ $num_agents -eq 1 ]; then
  num_rounds=1
  num_attempts=50
else
  num_rounds=6 
  num_attempts=3
fi  

onboarding_=$(printf '""%.0s,' $(seq 1 $num_agents) | sed 's/,$//')
save_dir=runs/$dataset/$(basename "${model_name,,}")/${num_agents}n

PORT0=$((10000 + RANDOM % 90000))
PORT=$((PORT0 + SLURM_ARRAY_TASK_ID))

echo "================================================"
echo "JOB ID:         $SLURM_JOB_ID"
echo "ARRAY TASK ID:  $SLURM_ARRAY_TASK_ID"
echo "PORT:           $PORT"
echo "ONBOARDING:     $onboarding_"
echo "n_ctx:          $n_ctx"
echo "================================================"

if [ ! -f ollama-linux-amd64.tgz ]; then
  curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz && tar -C ~/.local -xzf ollama-linux-amd64.tgz
fi
# Place this in ~/.bashrc to persist
export PATH=$HOME/.local/bin:$PATH && export LD_LIBRARY_PATH=$HOME/.local/lib/ollama:$LD_LIBRARY_PATH && ollama --version

# Enable multi-GPU usage
# export OLLAMA_NUM_PARALLEL=2
# export CUDA_VISIBLE_DEVICES=0,1
# export OLLAMA_GPU_OVERHEAD=0.5 

export OLLAMA_HOST="127.0.0.1:$PORT"
export OLLAMA_CONTEXT_LENGTH=$n_ctx

ollama serve &
sleep 5
ollama pull $model_name

echo "$(ollama ps)" 

mkdir -p $save_dir
echo python main.py $dataset $model_name $num_attempts $temperature $save_dir $num_rounds $onboarding_ $n_ctx
python main.py $dataset $model_name $num_attempts $temperature $save_dir $num_rounds $onboarding_ $n_ctx