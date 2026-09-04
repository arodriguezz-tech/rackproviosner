using RackProvisioner.UI.Components;
using RackProvisioner.UI;
using RackProvisioner.Core;
using RackProvisioner.Services;
using RackProvisioner.Services.AI;
using RackProvisioner.Data;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

builder.Services.AddHttpClient();

// Event bus for in-process pub/sub
builder.Services.AddSingleton<IEventBus, InMemoryEventBus>();

// Database context
builder.Services.AddDbContext<RackProvisionerDbContext>();

// Repositories
builder.Services.AddScoped<RackRepository>();
builder.Services.AddScoped<SwitchRepository>();

// Services
builder.Services.AddScoped<IInventoryService, InventoryService>();
builder.Services.AddScoped<ISkuService, SkuService>();
builder.Services.AddScoped<IDiscoveryService, DiscoveryService>();
builder.Services.AddScoped<IReadinessService, ReadinessService>();
builder.Services.AddSingleton<ISettingsService, SettingsService>();

// Register template-based explainer for readiness status
builder.Services.AddSingleton<IReadinessExplainer, TemplateExplainerService>();

// Readiness view model subscribes to readiness events and fetches explanations
builder.Services.AddSingleton<ReadinessViewModel>();

var app = builder.Build();

// Instantiate the view model to start subscriptions
app.Services.GetRequiredService<ReadinessViewModel>();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}
app.UseStatusCodePagesWithReExecute("/not-found", createScopeForStatusCodePages: true);
app.UseHttpsRedirection();

app.UseAntiforgery();

app.MapStaticAssets();
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
