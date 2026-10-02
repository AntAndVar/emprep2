import { ref, type ComputedRef, type Ref } from 'vue';
import type { Application, Draft } from '../types';

export interface AutosaveOptions {
  application: ComputedRef<Application | null>;
  draft: Ref<Draft>;
  /** Cancel queued autosaves while the host saves and submits the application. */
  paused: Ref<boolean>;
  onUpdated: (application: Application) => void;
}

/** TICKET 03 (optional): debounce genuine changes, save/restore, handle conflicts.
 * api.saveDraft and api.applications are supplied. A restore must be explicit.
 * Do not replace newer local edits with an earlier save's response.
 * Cancel pending debounce when paused is true; never save a submitted application.
 */
export function useDraftAutosave(options: AutosaveOptions) {
  const state = ref<'idle' | 'saving' | 'saved' | 'error' | 'conflict'>('idle');
  const message = ref('Autosave is an optional practice feature.');
  void options;
  async function saveNow() {
    // TODO(ticket-03): save the selected draft and its current server version.
    message.value = 'Ticket 03: implement draft saving here. Final submission already saves the draft.';
  }
  async function restore() {
    // TODO(ticket-03): fetch the latest server draft and restore only with consent.
    message.value = 'Ticket 03: implement an explicit restore of the saved draft.';
  }
  return { state, message, saveNow, restore };
}
