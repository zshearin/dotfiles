place="home"

eval "$(starship init zsh)"

alias gcb='git branch --show-current | tee >(pbcopy)'

gtask() {
  local title="$1"
  local notes="${2:-}"
  local list="c2N5ZnZ6eGRrTUNWLTFPVw"

  ensure_google_tasks_token

  curl -s -X POST \
    -H "Authorization: Bearer $GOOGLE_TASKS_TOKEN" \
    -H "Content-Type: application/json" \
    "https://tasks.googleapis.com/tasks/v1/lists/$list/tasks" \
    -d "$(jq -n --arg title "$title" --arg notes "$notes" \
    '{title: $title, notes: $notes}')" | jq
}


ensure_google_tasks_token() {
  local now
  now="$(date +%s)"

  if [[ -z "${GOOGLE_TASKS_TOKEN:-}" || \
       -z "${GOOGLE_TASKS_TOKEN_EXPIRES_AT:-}" || \
        "$now" -ge "$GOOGLE_TASKS_TOKEN_EXPIRES_AT" ]]; then
    export GOOGLE_TASKS_TOKEN="$(gcloud auth application-default print-access-token)"
    export GOOGLE_TASKS_TOKEN_EXPIRES_AT="$((now + 3300))" # refresh after ~55 minutes
  fi
}
