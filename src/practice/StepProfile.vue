<script setup lang="ts">
import type { Draft, FieldErrors } from '../types';
const model = defineModel<Draft>({ required: true });
defineProps<{ errors: FieldErrors }>();
</script>

<template>
  <div class="step-content">
    <span class="eyebrow">01 / CLIENT DETAILS</span><h2>A clear picture of your client.</h2><p class="step-description">Capture who is applying and how the account will be held.</p>
    <div class="form-grid">
      <div class="field full"><label for="legalName">Legal name</label><input id="legalName" v-model="model.legalName" autocomplete="name" :aria-invalid="!!errors.legalName" :aria-describedby="errors.legalName ? 'legalName-error' : undefined" /><p v-if="errors.legalName" id="legalName-error" class="field-error">{{ errors.legalName }}</p></div>
      <div class="field full"><label for="email">Email address</label><input id="email" v-model="model.email" type="email" autocomplete="email" :aria-invalid="!!errors.email" :aria-describedby="errors.email ? 'email-error' : undefined" /><p v-if="errors.email" id="email-error" class="field-error">{{ errors.email }}</p></div>
      <div class="field full"><label for="accountType">Account ownership</label><select id="accountType" v-model="model.accountType"><option value="individual">Individual account</option><option value="joint">Joint account</option></select></div>
      <!-- TODO(ticket-01): show this field only for a joint account. -->
      <div class="field full conditional-field"><label for="jointApplicantName">Joint applicant name <span>Conditional</span></label><input id="jointApplicantName" v-model="model.jointApplicantName" :aria-invalid="!!errors.jointApplicantName" :aria-describedby="errors.jointApplicantName ? 'jointApplicantName-error' : 'joint-hint'" /><p v-if="errors.jointApplicantName" id="jointApplicantName-error" class="field-error">{{ errors.jointApplicantName }}</p><p id="joint-hint" class="field-hint">Required for joint accounts. Conditional visibility is part of ticket 01.</p></div>
      <div class="field"><label for="employmentStatus">Employment</label><select id="employmentStatus" v-model="model.employmentStatus"><option value="employed">Employed</option><option value="self-employed">Self-employed</option><option value="retired">Retired</option></select></div>
      <div class="field"><label for="annualIncomeBand">Annual income band</label><select id="annualIncomeBand" v-model="model.annualIncomeBand"><option value="under-50k">Under $50,000</option><option value="50k-100k">$50,000–$100,000</option><option value="100k-plus">$100,000+</option></select></div>
    </div>
  </div>
</template>
