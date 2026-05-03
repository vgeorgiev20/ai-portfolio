using api.Models;
using Microsoft.EntityFrameworkCore;

namespace api;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options)
        : base(options)
    {
    }

    public DbSet<SemanticDocument> SemanticDocuments => Set<SemanticDocument>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasPostgresExtension("vector");

        modelBuilder.Entity<SemanticDocument>(entity =>
        {
            entity.ToTable("SemanticDocuments");
            entity.Property(e => e.Id).HasDefaultValueSql("gen_random_uuid()");
            entity.Property(e => e.Embedding).HasColumnType("vector(1536)");
            entity.Property(e => e.CreatedAt).HasDefaultValueSql("now()");
        });
    }
}
