import { fetchLead } from "@/lib/leads";
import { LeadDetail } from "@/components/lead-detail";

export default async function LeadDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const lead = await fetchLead(id);

  return <LeadDetail lead={lead} />;
}
