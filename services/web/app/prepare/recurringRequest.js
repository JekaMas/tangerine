// Pure request projection; form state retains hidden roles, payload does not.
export function recurringRequests(form) {
 return Array.from({length:Number(form.speakers)},(_,i)=>({profile:form.recurring?.[i],i})).filter(x=>x.profile?.enabled).map(({profile,i})=>({speaker_number:i+1,target_percent:Number(profile.percent??85),instruction:profile.instruction?.trim()||null}));
}
