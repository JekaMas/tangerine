import {failureMessage} from './failureMessage';

export default function SavedFailure({item}) {
  const message = failureMessage(item);
  return message ? <p className="error" role="alert">{message}</p> : null;
}
