export default function Navigation() {
  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-bold">Prompt Trainer</h1>
            <div className="hidden md:flex space-x-4">
              <a
                href="#papers"
                className="px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition"
              >
                Papers
              </a>
              <a
                href="#rubrics"
                className="px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition"
              >
                Rubrics
              </a>
              <a
                href="#evaluations"
                className="px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition"
              >
                Evaluations
              </a>
              <a
                href="#dashboard"
                className="px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition"
              >
                Dashboard
              </a>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
