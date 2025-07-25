import dynamic from "next/dynamic";

const FileManager = dynamic(() => import("../file-manager"), { ssr: false, loading: () => <div>Loading File Manager...</div> });

export default function FileManagerPage() {
  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">File Manager</h1>
      <FileManager />
    </div>
  );
}
