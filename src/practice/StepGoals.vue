<script setup lang="ts">
import type { Draft, FieldErrors } from '../types';
const model = defineModel<Draft>({ required: true });
defineProps<{ errors: FieldErrors }>();
// Keep horizonYears numeric, including the empty-field state (0).
function setHorizon(event: Event) { model.value.horizonYears = Number((event.target as HTMLInputElement).value); }
</script>

<template>
  <div class="step-content">
    <span class="eyebrow">02 / GOALS & FUNDING</span><h2>Understand the starting point.</h2><p class="step-description">Record the client's preferences and the origin of the proposed funding.</p>
    <div class="form-grid">
      <div class="field"><label for="objective">Primary objective</label><select id="objective" v-model="model.objective"><option value="growth">Long-term growth</option><option value="income">Income</option><option value="preservation">Capital preservation</option></select></div>
      <div class="field"><label for="riskComfort">Risk comfort</label><select id="riskComfort" v-model="model.riskComfort"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></div>
      <div class="field full"><label for="horizonYears">Time horizon, in years</label><input id="horizonYears" type="number" :value="model.horizonYears || ''" @input="setHorizon" :aria-invalid="!!errors.horizonYears" :aria-describedby="errors.horizonYears ? 'horizonYears-error' : 'horizon-hint'" /><p v-if="errors.horizonYears" id="horizonYears-error" class="field-error">{{ errors.horizonYears }}</p><p id="horizon-hint" class="field-hint">Use a whole number between 1 and 50 for this practice scenario.</p></div>
      <div class="field full"><label for="fundingSource">Funding source</label><select id="fundingSource" v-model="model.fundingSource"><option value="salary">Salary and savings</option><option value="business-sale">Business sale</option><option value="inheritance">Inheritance</option></select></div>
      <!-- TODO(ticket-01): show this field only when funding source is not salary. -->
      <div class="field full conditional-field"><label for="sourceDetails">Funding context <span>Conditional</span></label><textarea id="sourceDetails" v-model="model.sourceDetails" rows="3" :aria-invalid="!!errors.sourceDetails" :aria-describedby="errors.sourceDetails ? 'sourceDetails-error' : 'source-hint'" /><p v-if="errors.sourceDetails" id="sourceDetails-error" class="field-error">{{ errors.sourceDetails }}</p><p id="source-hint" class="field-hint">For a business sale or inheritance, add 10–500 characters of context.</p></div>
    </div>
  </div>
</template>
