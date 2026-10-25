// Turn browser transport failures into a recovery action, retaining native
// application messages and uncertain write outcomes. This performs no retry.
export function requestError(error, fallback='Could not reach the local service. Refresh saved state to check the outcome before retrying.') {
  if (error instanceof TypeError && /fetch|network|load failed/i.test(error.message)) return fallback;
  return error?.message || fallback;
}
