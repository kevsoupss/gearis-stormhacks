import "./Switch.css"; // put the CSS below in this file

interface SwitchProps {
    label: string,
    checked: boolean,
    setChecked: React.Dispatch<React.SetStateAction<boolean>>
}

export default function Switch({ label, checked, setChecked } : SwitchProps) {
  const handleToggle = () => setChecked((prev) => !prev);

  return (
    <div className="row-switch">
      <span className="switch-label">{label}</span>
      <label className="switch">
        <input
          type="checkbox"
          className="switch-input"
          checked={checked}
          onChange={handleToggle}
        />
        <span className="switch-track" aria-hidden="true"></span>
      </label>
    </div>
  );
}
