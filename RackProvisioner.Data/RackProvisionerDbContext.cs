using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.ChangeTracking;
using RackProvisioner.Domain;

namespace RackProvisioner.Data;

public class RackProvisionerDbContext : DbContext
{
    public DbSet<Rack> Racks { get; set; }
    public DbSet<Switch> Switches { get; set; }
    public DbSet<Configuration> Configurations { get; set; }
    public DbSet<ReadinessState> ReadinessStates { get; set; }

    public RackProvisionerDbContext(DbContextOptions<RackProvisionerDbContext> options)
        : base(options)
    {
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<Rack>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Serial).IsRequired().HasMaxLength(100);
            entity.Property(e => e.Position).IsRequired().HasMaxLength(50);
            entity.HasMany(e => e.Inventory)
                .WithOne(s => s.Rack)
                .HasForeignKey(s => s.RackId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<Switch>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Model).IsRequired().HasMaxLength(100);
            entity.Property(e => e.Serial).IsRequired().HasMaxLength(100);
            entity.Property(e => e.MAC).IsRequired().HasMaxLength(17);
            entity.HasOne(e => e.Rack)
                .WithMany(r => r.Inventory)
                .HasForeignKey(e => e.RackId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<Configuration>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(100);
            entity.Property(e => e.Description).IsRequired().HasMaxLength(100);
            entity.Property(e => e.Content).IsRequired();
            entity.Property(e => e.IsActive).HasDefaultValue(true);
            entity.HasOne(e => e.Rack)
                .WithMany()
                .HasForeignKey(e => e.RackId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<ReadinessState>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Status).IsRequired();
            entity.HasOne(e => e.Rack)
                .WithMany()
                .HasForeignKey(e => e.RackId)
                .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
