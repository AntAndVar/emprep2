<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue';
import { AlertCircle, ArrowLeft, ArrowRight, BookOpen, Check, CheckCircle2, ChevronRight, FileCheck2, FolderOpen, Leaf, LoaderCircle, RefreshCw, Save, ShieldCheck, Undo2, UserRound } from '@lucide/vue';
import type { Application, Draft, FieldErrors, WizardStep } from './types';
import { api, ApiError } from './lib/api';
import { dateLabel, documentProgress, initials, requiredDocumentKinds } from './lib/format';
import { validateStep } from './practice/wizard';
import { useDraftAutosave } from './practice/useDraftAutosave';
import StepProfile from './practice/StepProfile.vue';
import StepGoals from './practice/StepGoals.vue';
import DocumentReviewBoard from './practice/DocumentReviewBoard.vue';
import PracticeGuide from './components/PracticeGuide.vue';

const emptyDraft = (): Draft => ({ legalName: '', email: '', accountType: 'individual', jointApplicantName: '', employmentStatus: 'employed', annualIncomeBand: 'under-50k', fundingSource: 'salary', sourceDetails: '', objective: 'growth', riskComfort: 'medium', horizonYears: 0, consent: false });
const clone = <T,>(value: T): T => JSON.parse(JSON.stringify(value));
const applications = ref<Application[]>([]);
const selectedId = ref('');
const draft = ref<Draft>(emptyDraft());
const step = ref<WizardStep>(0);
const errors = ref<FieldErrors>({});
const view = ref<'workspace' | 'guide'>('workspace');
const loading = ref(true);
const loadError = ref('');
const submitError = ref('');
const submitting = ref(false);
const localDrafts = new Map<string, Draft>();
const selected = computed(() => applications.value.find(application => application.id === selectedId.value) ?? null);
const effectiveApplication = computed(() => selected.value ? { ...selected.value, draft: draft.value } : null);
const progress = computed(() => effectiveApplication.value ? documentProgress(effectiveApplication.value) : { verified: 0, total: 0, percent: 0 });
const dirty = computed(() => !!selected.value && JSON.stringify(draft.value) !== JSON.stringify(selected.value.draft));
const submittedCount = computed(() => applications.value.filter(application => application.status === 'submitted').length);
const documentLabels = { identity: 'Identity', address: 'Address', 'joint-identity': 'Joint applicant', 'source-of-funds': 'Source of funds' };
const objectives = { growth: 'Long-term growth', income: 'Income', preservation: 'Capital preservation' };
const sources = { salary: 'Salary and savings', 'business-sale': 'Business sale', inheritance: 'Inheritance' };

function updateApplication(application: Application) {
  applications.value = applications.value.map(existing => existing.id === application.id ? application : existing);
}
const autosave = useDraftAutosave({ application: selected, draft, paused: submitting, onUpdated: updateApplication });
const { state: saveState, message: saveMessage, saveNow, restore } = autosave;

function selectApplication(application: Application) {
  if (submitting.value) return;
  if (selectedId.value) localDrafts.set(selectedId.value, clone(draft.value));
  selectedId.value = application.id;
  draft.value = clone(localDrafts.get(application.id) ?? application.draft);
  step.value = 0;
  errors.value = {};
  submitError.value = '';
}

async function load(fail = false) {
  loading.value = true;
  loadError.value = '';
  try {
    const result = await api.applications(fail);
    applications.value = result.applications;
    if (result.applications.length) selectApplication(result.applications[0]);
    else selectedId.value = '';
  } catch (error) { loadError.value = error instanceof Error ? error.message : 'The applications could not load.'; }
  finally { loading.value = false; }
}

async function focusError() {
  await nextTick();
  const firstField = Object.keys(errors.value)[0];
  if (firstField) document.getElementById(firstField)?.focus();
}

async function advance() {
  errors.value = validateStep(draft.value, step.value);
  if (Object.keys(errors.value).length) { await focusError(); return; }
  step.value = Math.min(2, step.value + 1) as WizardStep;
  submitError.value = '';
}

function back() { step.value = Math.max(0, step.value - 1) as WizardStep; errors.value = {}; submitError.value = ''; }

async function submit() {
  if (!selected.value || submitting.value || saveState.value === 'saving') return;
  errors.value = validateStep(draft.value, 2);
  if (Object.keys(errors.value).length) {
    const profileFields = ['legalName', 'email', 'jointApplicantName'];
    const errorFields = Object.keys(errors.value);
    step.value = errorFields.some(field => profileFields.includes(field)) ? 0 : errorFields.some(field => ['horizonYears', 'sourceDetails'].includes(field)) ? 1 : 2;
    await focusError(); return;
  }
  if (progress.value.verified !== progress.value.total) { submitError.value = 'Verify all required document types before submitting.'; return; }
  const current = selected.value;
  submitting.value = true;
  submitError.value = '';
  let draftSaved = false;
  try {
    const saved = await api.saveDraft(current.id, clone(draft.value), current.version);
    updateApplication(saved.application);
    draftSaved = true;
    const result = await api.submit(current.id, saved.application.version);
    updateApplication(result.application);
    draft.value = clone(result.application.draft);
    localDrafts.delete(current.id);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Submission could not be completed.';
    submitError.value = `${draftSaved ? 'Your draft was saved. ' : ''}${message}${error instanceof ApiError && error.status === 409 ? ' Keep your local input and resolve the version conflict before retrying.' : ''}`;
  } finally { submitting.value = false; }
}

onMounted(() => void load(new URLSearchParams(window.location.search).get('fail') === '1'));
</script>

<template>
  <div class="app">
    <header class="main-header"><a href="#" class="brand" @click.prevent="view = 'workspace'"><span class="brand-symbol"><Leaf :size="23" /></span><strong>entry<span>.</span></strong><span class="brand-divider" /><span class="brand-subtitle">Private wealth onboarding</span></a><nav aria-label="Main navigation"><button :class="{ active: view === 'workspace' }" @click="view = 'workspace'"><FolderOpen :size="17" />Workspace</button><button :class="{ active: view === 'guide' }" @click="view = 'guide'"><BookOpen :size="17" />Practice guide</button></nav><span class="practice-tag">Practice 02</span></header>
    <PracticeGuide v-if="view === 'guide'" />
    <main v-else>
      <div class="page-top"><div><div class="breadcrumb">Northstar Wealth <ChevronRight :size="13" /> Client onboarding</div><h1>From first conversation to ready.</h1><p>Prepare the application, review the evidence, and hand over a clear next step.</p></div><div class="scenario-date"><span>SCENARIO DATE</span><strong>October 3, 2026</strong><small>Synthetic records only</small></div></div>
      <section v-if="loading" class="loading-panel" role="status"><LoaderCircle class="spin" :size="28" /><h2>Loading applications…</h2></section>
      <section v-else-if="loadError" class="error-panel" role="alert"><AlertCircle :size="30" /><h2>The workspace could not load</h2><p>{{ loadError }}</p><button class="button primary" @click="load(false)"><RefreshCw :size="16" />Try again</button></section>
      <section v-else-if="!selected" class="empty-panel"><FolderOpen :size="30" /><h2>No applications yet</h2><p>No client applications were returned by the practice API.</p></section>
      <div v-else class="workspace-grid">
        <aside class="applications-panel" aria-labelledby="applications-heading"><div class="list-heading"><h2 id="applications-heading">Applications <span>{{ applications.length }}</span></h2><p>{{ applications.length - submittedCount }} in progress · {{ submittedCount }} submitted</p></div><div class="application-list"><button v-for="application in applications" :key="application.id" :class="['application-card', { selected: selectedId === application.id }]" :aria-pressed="selectedId === application.id" :disabled="submitting" @click="selectApplication(application)"><span class="client-initials">{{ initials(application.clientName) }}</span><div><strong>{{ application.clientName }}</strong><span>{{ application.draft.accountType === 'joint' ? 'Joint account' : 'Individual account' }}</span><small>{{ application.status === 'submitted' ? 'Submitted' : `${documentProgress(application).verified}/${documentProgress(application).total} document types verified` }}</small></div><ChevronRight :size="16" /></button></div><div class="list-note"><ShieldCheck :size="19" /><strong>A focused practice round</strong><p>Use Chen for a straightforward review, Rivera for conditional fields, or Park for incomplete data.</p><button @click="view = 'guide'">Read the feature briefs <ArrowRight :size="14" /></button></div></aside>
        <section class="wizard-panel" aria-labelledby="wizard-heading">
          <header class="wizard-header"><div><span class="eyebrow">APPLICATION / {{ selected.id }}</span><h2 id="wizard-heading">{{ selected.clientName }}</h2></div><span :class="['status-chip', selected.status === 'submitted' ? 'verified' : '']">{{ selected.status === 'submitted' ? 'Submitted' : 'Draft' }}</span></header>
          <ol class="stepper" aria-label="Application progress"><li v-for="(label, index) in ['Client details', 'Goals & funding', 'Review']" :key="label" :class="{ current: step === index, passed: step > index }" :aria-current="step === index ? 'step' : undefined"><span><Check v-if="step > index" :size="14" /><template v-else>{{ index + 1 }}</template></span><strong>{{ label }}</strong></li></ol>
          <div v-if="selected.status === 'submitted'" class="submitted-panel" role="status"><span><CheckCircle2 :size="38" /></span><h2>Application submitted.</h2><p>The draft and document decisions are saved. This application is now read-only.</p><div><strong>{{ selected.clientName }}</strong><small>Recorded {{ dateLabel(selected.updatedAt) }} · Version {{ selected.version }}</small></div></div>
          <form v-else novalidate @submit.prevent="step < 2 ? advance() : submit()">
            <fieldset :disabled="submitting">
              <div class="feature-strip"><span>Ticket 01</span>Step validation and conditional fields are your first feature.</div>
              <p v-if="Object.keys(errors).length" class="validation-summary" role="alert">Please correct the highlighted fields before continuing.</p>
              <StepProfile v-if="step === 0" v-model="draft" :errors="errors" />
              <StepGoals v-else-if="step === 1" v-model="draft" :errors="errors" />
              <div v-else class="step-content review-content"><span class="eyebrow">03 / REVIEW & HANDOVER</span><h2>Bring the application together.</h2><p class="step-description">Review the client’s details and confirm each required document before submitting.</p><dl class="review-summary"><div><dt>Applicant</dt><dd>{{ draft.legalName || 'Not provided' }}<small>{{ draft.email || 'Email not provided' }}</small></dd></div><div><dt>Ownership</dt><dd>{{ draft.accountType === 'joint' ? `Joint · ${draft.jointApplicantName || 'Name missing'}` : 'Individual' }}</dd></div><div><dt>Objective</dt><dd>{{ objectives[draft.objective] }} · {{ draft.horizonYears || '—' }} years</dd></div><div><dt>Funding</dt><dd>{{ sources[draft.fundingSource] }}</dd></div></dl><DocumentReviewBoard v-if="effectiveApplication" :application="effectiveApplication" @updated="updateApplication" /><label class="consent-field" for="consent"><input id="consent" v-model="draft.consent" type="checkbox" :aria-invalid="!!errors.consent" :aria-describedby="errors.consent ? 'consent-error' : undefined" /><span>I confirm the fictional client information has been reviewed and the client has agreed to this practice submission.</span></label><p v-if="errors.consent" id="consent-error" class="field-error">{{ errors.consent }}</p></div>
              <p v-if="submitError" class="submit-error" role="alert">{{ submitError }}</p>
              <footer class="wizard-footer"><button v-if="step > 0" type="button" class="button secondary" @click="back"><ArrowLeft :size="16" />Back</button><span v-else class="form-footnote">All fields use fictional practice rules.</span><button v-if="step < 2" type="submit" class="button primary">Continue <ArrowRight :size="17" /></button><button v-else type="submit" class="button primary" :disabled="submitting || saveState === 'saving' || progress.verified !== progress.total"><LoaderCircle v-if="submitting" class="spin" :size="17" /><CheckCircle2 v-else :size="17" />{{ submitting ? 'Saving and submitting…' : 'Submit application' }}</button></footer>
            </fieldset>
          </form>
        </section>
        <aside class="readiness-panel"><div class="readiness-header"><span class="readiness-icon"><FileCheck2 :size="24" /></span><span class="eyebrow">APPLICATION READINESS</span><h2>Every detail counts.</h2><p>A clear checklist makes the next action easier to see.</p></div><div class="readiness-progress"><div><strong>{{ progress.verified }}<span>/{{ progress.total }}</span></strong><small>Required document types verified</small></div><div class="progress-track" role="progressbar" aria-label="Document verification" :aria-valuenow="progress.percent" :aria-valuemin="0" :aria-valuemax="100"><span :style="{ width: `${progress.percent}%` }" /></div></div><ul class="readiness-checklist"><li v-for="kind in requiredDocumentKinds(draft)" :key="kind"><CheckCircle2 v-if="selected.documents.some(document => document.kind === kind && document.status === 'verified')" class="done" :size="17" /><span v-else class="unchecked" /><span>{{ documentLabels[kind] }}</span></li></ul><div class="advisor-detail"><UserRound :size="18" /><div><span>Assigned advisor</span><strong>{{ selected.assignedAdvisor }}</strong></div></div><div class="draft-saving"><div class="section-heading"><h3>Draft continuity</h3><span class="ticket-label">03</span></div><p v-if="selected.status === 'submitted'">Submitted applications are read-only.</p><template v-else><p>{{ dirty ? 'Local edits have not been saved.' : 'Showing the saved server draft.' }}</p><div class="save-controls"><button class="button secondary" :disabled="submitting || saveState === 'saving'" @click="saveNow"><Save :size="14" />Save draft</button><button class="icon-button" title="Restore saved draft — ticket 03" aria-label="Restore saved draft" :disabled="submitting || saveState === 'saving'" @click="restore"><Undo2 :size="17" /></button></div><small role="status">{{ saveMessage }}</small></template></div><div class="record-meta"><span>Saved record</span><strong>Version {{ selected.version }}</strong><small>{{ dateLabel(selected.updatedAt) }}</small></div></aside>
      </div>
      <footer class="page-footer"><span>Independent assessment practice · Vue + TypeScript / Python</span><button @click="view = 'guide'">Feature briefs <BookOpen :size="14" /></button></footer>
    </main>
  </div>
</template>
