type Tab = 'papers' | 'rubrics' | 'evaluations';

interface Props {
  activeTab: Tab;
  onChange: (tab: Tab) => void;
}

export default function Navigation({ activeTab, onChange }: Props) {
  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-bold">Prompt Trainer</h1>
            <div className="hidden md:flex space-x-2">
              {[
                { key: 'papers', label: 'Papers' },
                { key: 'rubrics', label: 'Rubrics' },
                { key: 'evaluations', label: 'Evaluations' },
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => onChange(tab.key as Tab)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                    activeTab === tab.key
                      ? 'bg-white text-blue-700'
                      : 'hover:bg-blue-700'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
