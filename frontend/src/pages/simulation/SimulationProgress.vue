<template>
  <div class="w-full max-w-xl flex flex-col gap-4 items-center">
    <ProgressSpinner v-if="!isCancelled && !isFailed" />
    <i
      v-else-if="isCancelled"
      class="pi pi-stop-circle text-4xl text-orange-500"
      aria-hidden="true"
    />
    <i
      v-else
      class="pi pi-times-circle text-4xl text-red-500"
      aria-hidden="true"
    />
    <div v-if="!isCancelled && !isFailed" class="w-full flex flex-col gap-2">
      <ProgressBar :value="progressPercent" :show-value="true" />
      <span
        v-if="currentStepLabel"
        class="text-sm text-surface-600 dark:text-surface-300 text-center"
      >
        {{ currentStepLabel }}
      </span>
    </div>
    <ul class="w-full flex flex-col gap-2 mt-1">
      <li
        v-for="step in steps"
        :key="step.id"
        class="flex flex-row items-center gap-3 text-sm"
        :class="stepClass(step)"
      >
        <i :class="stepIcon(step)" />
        <span class="flex flex-row items-center gap-2 min-w-0">
          <span
            v-if="stepDuration(step)"
            class="tabular-nums text-surface-500 dark:text-surface-400 shrink-0"
          >
            {{ stepDuration(step) }}
          </span>
          <span class="truncate">{{ step.label }}</span>
        </span>
      </li>
    </ul>
    <Message
      v-if="isCancelled"
      severity="warn"
      :closable="false"
      class="w-full"
    >
      Simulation stopped.
    </Message>
    <Message
      v-else-if="failedStep"
      severity="error"
      :closable="false"
      class="w-full"
    >
      Simulation failed at: <strong>{{ failedStep.label }}</strong>
      <span v-if="errorMessage"> — {{ errorMessage }}</span>
    </Message>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import type {
  SimulationProgress,
  SimulationProgressStep,
} from '@/backend/interfaces'

const props = defineProps<{
  progress: SimulationProgress | null | undefined
}>()

const tick = ref(0)
const tickTimer = setInterval(() => {
  if (!props.progress?.cancelled) {
    tick.value += 1
  }
}, 1000)

onUnmounted(() => clearInterval(tickTimer))

const isCancelled = computed(() => props.progress?.cancelled === true)

const isFailed = computed(
  () => !isCancelled.value && !!props.progress?.failed_at,
)

const steps = computed(() => props.progress?.steps ?? defaultSteps())

const progressPercent = computed(() => props.progress?.progress_percent ?? 0)

const currentStepLabel = computed(() => {
  if (isCancelled.value) return null
  if (progressPercent.value >= 100 && !props.progress?.current_step) {
    return 'Finishing'
  }
  if (!props.progress?.current_step) return 'Starting simulation...'
  const step = steps.value.find(s => s.id === props.progress?.current_step)
  if (step?.status === 'failed') return `${step.label} failed`
  if (step?.status === 'in_progress') {
    const duration = stepDurationLive(step)
    return duration ? `${duration} — ${step.label}` : step.label
  }
  return step?.label ?? 'Starting simulation...'
})

const failedStep = computed(() => {
  if (isCancelled.value || !props.progress?.failed_at) return null
  return steps.value.find(s => s.id === props.progress?.failed_at) ?? null
})

const errorMessage = computed(() => props.progress?.error_message ?? null)

watch(tick, () => undefined)

function defaultSteps(): SimulationProgressStep[] {
  return [
    {
      id: 'building_model',
      label: 'Building Pyomo model',
      status: 'in_progress',
    },
    { id: 'optimizing', label: 'Running optimization', status: 'pending' },
    {
      id: 'preparing_dashboard',
      label: 'Preparing result dashboard',
      status: 'pending',
    },
  ]
}

function formatDurationCompleted(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  const minutes = Math.floor(seconds / 60)
  const remainder = Math.floor(seconds % 60)
  return `${minutes}m ${remainder}s`
}

function formatDurationLive(seconds: number): string {
  if (seconds < 60) return `${Math.floor(seconds)}s`
  const minutes = Math.floor(seconds / 60)
  const remainder = Math.floor(seconds % 60)
  return `${minutes}m ${remainder}s`
}

function elapsedSeconds(startedAt: string): number | null {
  const started = Date.parse(startedAt)
  if (Number.isNaN(started)) return null
  return Math.max(0, (Date.now() - started) / 1000)
}

function stepDurationLive(step: SimulationProgressStep): string | null {
  void tick.value
  if (step.status === 'in_progress' && step.started_at) {
    const elapsed = elapsedSeconds(step.started_at)
    if (elapsed != null) return formatDurationLive(elapsed)
  }
  return null
}

function stepDuration(step: SimulationProgressStep): string | null {
  void tick.value
  if (step.duration_seconds != null) {
    return formatDurationCompleted(step.duration_seconds)
  }
  if (step.status === 'in_progress' && step.started_at) {
    const elapsed = elapsedSeconds(step.started_at)
    if (elapsed != null) return formatDurationLive(elapsed)
  }
  return null
}

function stepIcon(step: SimulationProgressStep): string {
  switch (step.status) {
    case 'completed':
      return 'pi pi-check-circle text-green-500'
    case 'in_progress':
      return 'pi pi-spin pi-spinner text-primary'
    case 'failed':
      return 'pi pi-times-circle text-red-500'
    case 'cancelled':
      return 'pi pi-stop-circle text-orange-500'
    default:
      return 'pi pi-circle text-surface-400'
  }
}

function stepClass(step: SimulationProgressStep): string {
  if (step.status === 'failed') return 'text-red-600 dark:text-red-400'
  if (step.status === 'cancelled')
    return 'text-surface-500 dark:text-surface-400 line-through'
  if (step.status === 'completed')
    return 'text-surface-700 dark:text-surface-200'
  if (step.status === 'in_progress') return 'text-primary font-medium'
  return 'text-surface-500 dark:text-surface-400'
}
</script>

<style scoped></style>
