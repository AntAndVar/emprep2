<script setup lang="ts">
import { FileCheck2, Files } from '@lucide/vue';
import type { Application } from '../types';
import { requiredDocumentKinds } from '../lib/format';

defineProps<{ application: Application }>();
defineEmits<{ updated: [application: Application] }>();
const labels = { identity: 'Identity document', address: 'Proof of address', 'joint-identity': 'Joint applicant identity', 'source-of-funds': 'Source of funds' };
// TODO(ticket-02): replace this read-only preview with a review board.
// Keep required-but-missing documents visible; emit only a confirmed saved response.
</script>

<template>
  <section class="document-slot" aria-labelledby="documents-heading">
    <div class="section-heading"><div><span class="eyebrow">FEATURE TICKET 02</span><h3 id="documents-heading">Document review</h3></div><Files :size="22" /></div>
    <p class="helper">Build a checklist or status board that lets the advisor verify received documents or reject them with a reason.</p>
    <ul class="document-preview">
      <li v-for="kind in requiredDocumentKinds(application.draft)" :key="kind"><FileCheck2 :size="18" /><div><strong>{{ labels[kind] }}</strong><span>{{ application.documents.find(document => document.kind === kind)?.name ?? 'No document on file' }}</span></div><span class="status-chip">{{ application.documents.find(document => document.kind === kind)?.status ?? 'Missing' }}</span></li>
    </ul>
    <div class="slot-callout">The supplied API saves document decisions. Review controls are your practice feature.</div>
  </section>
</template>
