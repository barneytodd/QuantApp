import {useEffect, useState} from "react"

export default function CustomTextBox({
    strategyType,
    customStrategy,
    setCustomStrategy,
    strategyOptions,
    visible,
    setVisible,
}) { 
    const [rawText, setRawText] = useState("");

    const buildDefaultStrategies = (options) =>
    options
        .filter((s) => s.value !== "custom")
        .map((s) => ({
        label: s.label,
        name: s.value,
        symbols: [],
        weights: [],
        }));

    const strategiesToText = (strategies) =>
    strategies
      .map(
        (s) =>
          `${s.label}\nsymbols: [${s.symbols.join(", ")}]\nweights: [${s.weights.join(", ")}]\n------------`
      )
      .join("\n");


    // Parse textarea text back into structured objects
    const parseTextToStrategies = (text, originalStrategies) => {
        const blocks = text.split("------------").map((b) => b.trim()).filter(Boolean);
        return blocks.map((block, index) => {
            const lines = block.split("\n").map((l) => l.trim());
            const label = lines[0] || "";
            const symbolsLine = lines.find((l) => l.startsWith("symbols:")) || "symbols: []";
            const weightsLine = lines.find((l) => l.startsWith("weights:")) || "weights: []";

            // Convert string arrays to real arrays
            const symbols = symbolsLine
                .replace("symbols:", "")
                .replace("[", "")
                .replace("]", "")
                .split(",")
                .map((s) => s.trim())
                .filter(Boolean);

            const weights = weightsLine
                .replace("weights:", "")
                .replace("[", "")
                .replace("]", "")
                .split(",")
                .map((w) => parseFloat(w.trim()))
                .filter((w) => !isNaN(w));
            
            const name = originalStrategies?.[index]?.name ?? "";

            return { label, name, symbols, weights };
        });
    };

    useEffect(() => {
        if (strategyType?.value === "custom") {
            const defaultStrats = buildDefaultStrategies(strategyOptions)
            setCustomStrategy(defaultStrats);
            setRawText(strategiesToText(defaultStrats))
        }
    }, [strategyOptions, strategyType?.value, setCustomStrategy]);

    if (strategyType?.value !== "custom") return null;

    return (
        <div className="bg-white shadow rounded-xl p-4 col-span-1 md:col-span-2">
            <div
                className="flex justify-between items-center cursor-pointer"
                onClick={() => setVisible((v) => !v)}
            >
                <h3 className="text-lg font-semibold mb-3">Input Custom Strategy</h3>
                <span>{visible ? "▲" : "▼"}</span>
            </div>

            {/* Custom Text Box (textarea) */}
            {visible && (
                <textarea
                    value={rawText}
                    onChange={(e) => setRawText(e.target.value) }
                    onBlur={() => {
                        const parsed = parseTextToStrategies(rawText, customStrategy);
                        setCustomStrategy(parsed);
                    }}
                    className="border p-2 rounded w-full h-[25em] resize-none font-mono"
                />
            )}
        </div>
    )
}