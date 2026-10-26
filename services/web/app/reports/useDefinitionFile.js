'use client';
import {useEffect,useRef,useState} from 'react';
import {createDefinitionFile} from './definitionFile';

export default function useDefinitionFile(onValue) {
  const [error,onError]=useState('');
  const owner=useRef(null);
  if(!owner.current)owner.current=createDefinitionFile({onValue,onError});
  useEffect(()=>()=>owner.current.cancel(),[]);
  return {error,...owner.current};
}
