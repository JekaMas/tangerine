package app

// Materialize only safe counters in the preparation's existing CAS write. List
// readback remains PostgreSQL-only and never depends on private media readiness.
func speechProgressSummary(progress map[string]any) map[string]any {
	counter := map[string]any{"complete_pieces": 0, "total_pieces": 0, "first_unfinished_piece": nil, "ready_to_assemble": false}
	if progress == nil {
		return counter
	}
	pieces := progress["pieces"].([]any)
	complete := 0
	for _, v := range pieces {
		piece := v.(map[string]any)
		if piece["state"] == "complete" {
			complete++
		} else if counter["first_unfinished_piece"] == nil {
			counter["first_unfinished_piece"] = piece["id"]
		}
	}
	counter["total_pieces"] = len(pieces)
	counter["complete_pieces"] = complete
	counter["ready_to_assemble"] = len(pieces) > 0 && complete == len(pieces)
	return counter
}
