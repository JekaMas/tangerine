// Presentation of accepted native outcomes, never a new admission check.
export const cleanupStatus=state=>({
  preview:'Preview ready',
  blocked_active_reference:'Still in use',
  native_erased:'Local records deleted; external cleanup remains',
  native_erased_media_cleanup_pending:'Local records deleted; media cleanup remains',
  erased:'Deletion complete',
}[state]||'Cleanup needs attention');
export const labCleanupStatus=state=>({
  not_requested:'No external cleanup requested',
  pending_explicit_local_lab_cleanup:'External Lab cleanup remains',
  erased:'External copies deleted',
}[state]||'Check external cleanup in Recovery');
