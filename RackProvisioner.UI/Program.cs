using RackProvisioner.UI.Components;
using RackProvisioner.UI;
using RackProvisioner.Core;
using RackProvisioner.Services.AI;
using RackProvisioner.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

builder.Services.AddHttpClient();

// Event bus for in-process pub/sub
builder.Services.AddSingleton<IEventBus, InMemoryEventBus>();

// Register explainer: use Gemini if GEMINI_API_KEY is set, otherwise templates
builder.Services.AddSingleton<IReadinessExplainer>(sp =>
{
    var apiKey = Environment.GetEnvironmentVariable("GEMINI_API_KEY");
    var httpClient = sp.GetRequiredService<HttpClient>();
    if (!string.IsNullOrEmpty(apiKey))
    {
        return new GeminiExplainerService(apiKey, httpClient);
    }
    return new TemplateExplainerService();
});

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
