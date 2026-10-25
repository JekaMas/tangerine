import {needsRecordIdentity} from './savedRecord';

export default function RecordIdentity({item, items, dateField}) {
  return needsRecordIdentity(item, items, dateField)
    ? <p className="record-identity">Record: {item.id}</p> : null;
}
