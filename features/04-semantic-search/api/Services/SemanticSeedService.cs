using api.Models;
using Microsoft.EntityFrameworkCore;
using Pgvector;

namespace api.Services;

public sealed class SemanticSeedService(
    AppDbContext db,
    IEmbeddingService embedding)
{
    private static readonly (string Title, string Content)[] Documents =
    [
        ("Breach of Contract - Failure to Deliver",
            "The supplier failed to deliver goods by the agreed date despite written confirmation. The client suffered financial loss due to project delays caused by this breach. Under Australian contract law, the non-breaching party is entitled to damages that naturally flow from the breach."),
        ("Negligence and Duty of Care",
            "A property owner has a duty of care to ensure their premises are safe for visitors. Failure to repair a known hazard that results in injury may constitute negligence. The plaintiff must establish that the duty existed, was breached, and caused measurable harm."),
        ("Unfair Dismissal Claim",
            "An employee was terminated without notice or a valid performance improvement plan. The dismissal was found to be harsh and unreasonable under the Fair Work Act. The employee was awarded compensation and reinstatement was considered."),
        ("Intellectual Property - Copyright Infringement",
            "A competitor reproduced proprietary marketing materials without authorisation. Copyright subsists automatically in original works under Australian law without registration. The rights holder may seek injunctive relief and damages for the unauthorised reproduction."),
        ("Property Settlement After Separation",
            "Following the breakdown of a de facto relationship, both parties sought a division of jointly held property. The court considered contributions made by each party, both financial and non-financial. A 60/40 split was ordered in favour of the primary income earner."),
        ("Personal Injury - Motor Vehicle Accident",
            "The claimant sustained whiplash injuries after a rear-end collision at a traffic intersection. Liability was admitted by the at-fault driver's insurer. Compensation was sought for medical expenses, lost income, and general damages for pain and suffering."),
        ("Defamation - False Statements Online",
            "A former client posted false and damaging reviews about a business on multiple public platforms. The statements were found to be defamatory as they caused serious harm to the business's reputation. A takedown order and damages were pursued under the Defamation Act."),
        ("Workplace Harassment and Bullying",
            "An employee reported repeated targeted behaviour by a manager including public humiliation and exclusion from meetings. The employer failed to investigate the formal complaint within a reasonable timeframe. The employee lodged an application with the Fair Work Commission for an anti-bullying order."),
        ("Misleading and Deceptive Conduct",
            "A vendor made false representations about the performance capabilities of software sold to a business client. The conduct contravened the Australian Consumer Law prohibitions on misleading conduct in trade. The client sought rescission of the contract and a full refund."),
        ("Lease Dispute - Commercial Tenancy",
            "A commercial tenant withheld rent following the landlord's refusal to carry out essential repairs affecting business operations. The lease agreement placed maintenance obligations on the landlord for structural elements. Mediation was recommended before proceeding to the tribunal."),
        ("Director Duty Breach - Insolvent Trading",
            "A company director continued to incur debts after becoming aware the company was insolvent. Under the Corporations Act, directors have a duty to prevent insolvent trading. The liquidator pursued the director personally for debts incurred during the insolvent period."),
        ("Estate Dispute - Contesting a Will",
            "An adult child of the deceased was excluded from the will despite being financially dependent on the estate. The Family Provision Act allows eligible persons to apply for adequate provision from the estate. The court assessed the claimant's financial need and the size of the estate."),
        ("Consumer Guarantee - Faulty Goods",
            "A consumer purchased a refrigerator that stopped functioning within three months of delivery. Under the Australian Consumer Law, major failures entitle the consumer to a refund or replacement. The retailer's attempt to limit liability through a shorter warranty clause was found unenforceable."),
        ("Privacy Breach - Unauthorised Data Disclosure",
            "A medical practice disclosed patient records to a third party without consent. The Privacy Act 1988 and Australian Privacy Principles govern the handling of sensitive health information. The Office of the Australian Information Commissioner investigated and required the practice to update its data handling procedures."),
        ("Construction Dispute - Defective Workmanship",
            "A homeowner engaged a builder for a renovation that was completed with significant structural defects. The builder refused to return and rectify the defective work within a reasonable time. The homeowner sought compensation through the Queensland Building and Construction Commission.")
    ];

    public async Task SeedAsync(CancellationToken ct = default)
    {
        if (await db.SemanticDocuments.AnyAsync(ct))
        {
            return;
        }

        foreach (var (title, content) in Documents)
        {
            var floats = await embedding.GetEmbeddingAsync(content, ct);
            db.SemanticDocuments.Add(new SemanticDocument
            {
                Title = title,
                Content = content,
                Embedding = new Vector(floats),
                CreatedAt = DateTime.UtcNow
            });
        }

        await db.SaveChangesAsync(ct);
    }
}
