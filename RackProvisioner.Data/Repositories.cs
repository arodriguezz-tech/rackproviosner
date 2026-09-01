using RackProvisioner.Domain;
using Microsoft.EntityFrameworkCore;

namespace RackProvisioner.Data;

public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(int id);
    Task SaveAsync();
}

public class RackRepository : IRepository<Rack>
{
    private readonly RackProvisionerDbContext _context;

    public RackRepository(RackProvisionerDbContext context)
    {
        _context = context;
    }

    public async Task<Rack?> GetByIdAsync(int id)
    {
        return await _context.Racks.FindAsync(id);
    }

    public async Task<Rack?> GetBySerialAsync(string serial)
    {
        return await _context.Racks.FirstOrDefaultAsync(r => r.Serial == serial);
    }

    public async Task<IEnumerable<Rack>> GetAllAsync()
    {
        return await _context.Racks.ToListAsync();
    }

    public async Task AddAsync(Rack entity)
    {
        await _context.Racks.AddAsync(entity);
    }

    public async Task UpdateAsync(Rack entity)
    {
        _context.Racks.Update(entity);
        await Task.CompletedTask;
    }

    public async Task DeleteAsync(int id)
    {
        var rack = await GetByIdAsync(id);
        if (rack != null)
        {
            _context.Racks.Remove(rack);
        }
    }

    public async Task SaveAsync()
    {
        await _context.SaveChangesAsync();
    }
}

public class SwitchRepository : IRepository<Switch>
{
    private readonly RackProvisionerDbContext _context;

    public SwitchRepository(RackProvisionerDbContext context)
    {
        _context = context;
    }

    public async Task<Switch?> GetByIdAsync(int id)
    {
        return await _context.Switches.FindAsync(id);
    }

    public async Task<IEnumerable<Switch>> GetByRackIdAsync(int rackId)
    {
        return await _context.Switches.Where(s => s.RackId == rackId).ToListAsync();
    }

    public async Task<IEnumerable<Switch>> GetAllAsync()
    {
        return await _context.Switches.ToListAsync();
    }

    public async Task AddAsync(Switch entity)
    {
        await _context.Switches.AddAsync(entity);
    }

    public async Task UpdateAsync(Switch entity)
    {
        _context.Switches.Update(entity);
        await Task.CompletedTask;
    }

    public async Task DeleteAsync(int id)
    {
        var @switch = await GetByIdAsync(id);
        if (@switch != null)
        {
            _context.Switches.Remove(@switch);
        }
    }

    public async Task SaveAsync()
    {
        await _context.SaveChangesAsync();
    }
}
