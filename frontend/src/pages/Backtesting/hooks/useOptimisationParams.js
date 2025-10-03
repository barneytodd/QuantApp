import { useState, useEffect } from "react";
import { optimisationParams } from "../parameters/optimisationParams";

export function useOptimisationParams() {
  const [optimParams, setOptimParams] = useState({});


  useEffect(() => {
    const params = [
    ...optimisationParams,
    ];
    const defaults = Object.fromEntries(
        params.map((p) => [
            p.name,
            { value: p.default, label: p.label, type: p.type },
    ]))
    setOptimParams(defaults);
  }, []);

  return {
    optimParams,
    setOptimParams,
  };
}
