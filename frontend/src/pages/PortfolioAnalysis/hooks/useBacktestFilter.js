import { useState, useEffect } from "react";

export function useBacktestFilter(uniFilterResults) {
    if (!uniFilterResults) return;

    const symbols = uniFilterResults.map(s => s.value)

    
}