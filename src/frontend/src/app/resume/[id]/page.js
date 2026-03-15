import ResumePage from '../page';


export default async function ResumeEditPage({ params }) {
  const resolvedParams = await params;
  return <ResumePage resumeId={resolvedParams.id} />;
}