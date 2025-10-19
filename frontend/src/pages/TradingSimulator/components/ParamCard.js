export default function ParamCard({param, setParam}) {
    return (
        <div className="bg-white shadow rounded-xl p-4">
            
            {/* Tooltip container */}
            <div className="relative group">
                <h3 className="text-lg font-semibold mb-3">{param?.label}</h3>
                
                {/* Tooltip text */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-40 bg-gray-800 text-white text-sm p-2 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 whitespace-pre-line">
                    {param?.info}
                </div>
            </div>
            <div>
                <input
                type={param?.type}
                value={param?.value ?? ""}
                onChange={(e) =>
                    setParam((prev) => ({ ...prev, value: e.target.value }))
                }
                onBlur={(e) =>
                    setParam((prev) => ({ ...prev, value: Number(e.target.value) || 0 }))
                }
                className="border p-1 rounded"
                />
            </div>
        </div>
    )
}