import { components } from "react-select"

// Option with a readonly checkbox
export const Option = (props) => (
<components.Option {...props}>
    <input
    type="checkbox"
    checked={props.isSelected}
    readOnly
    style={{ marginRight: 8 }}
    />
    <span>{props.label}</span>
</components.Option>
);

// MenuList that adds a Select all / Clear all control at the top
export const MenuList = (props) => {
    const { options } = props; 
    const { value = [], onChange } = props.selectProps; 

    const allSelected = value.length === options.length && options.length > 0;

    const toggleSelectAll = (e) => {
    // prevent the menu from closing and the click from bubbling
    e.preventDefault();
    e.stopPropagation();

    if (allSelected) {
        // clear selection
        onChange([], { action: "clear" });
    } else {
        // select all options 
        onChange(options, { action: "select-option" });
    }
    };

    return (
    <components.MenuList {...props}>
        <div
        style={{
            padding: 8,
            borderBottom: "1px solid #eee",
            position: "sticky",
            top: 0,
            background: "white",
            zIndex: 1,
        }}
        >
        <button
            type="button"
            onMouseDown={(e) => toggleSelectAll(e)}
            style={{
            cursor: "pointer",
            border: "none",
            background: "transparent",
            padding: 0,
            fontWeight: 600,
            color: "#2563eb",
            }}
        >
            {allSelected ? "Clear all" : "Select all"}
        </button>
        </div>

        {props.children}
    </components.MenuList>
    );
};