<#
  Volta a mostrar janelas que o GlazeWM deixou escondidas ("cloaked") ao sair.

  O GlazeWM esconde as janelas dos workspaces que não estão à vista com uma
  interface interna do Windows (IApplicationView::SetCloak). Ao sair, o
  processo de vigia dele devia mostrá-las de novo, mas na 3.10.1 isso falha às
  vezes para janelas de workspaces escondidos: ficam abertas e invisíveis.

  Corre em shutdown_commands do GlazeWM com -WaitForGlazeExit: espera que o
  glazewm.exe termine e só depois atua. Ignora janelas do próprio Windows
  (barra de tarefas, Iniciar, apps da Store suspensas), que estão escondidas
  de propósito.

  Uso manual (se alguma janela "desaparecer"):
    powershell -NoProfile -ExecutionPolicy Bypass -File uncloak.ps1
#>
param([switch]$WaitForGlazeExit)

if ($WaitForGlazeExit) {
  for ($i = 0; $i -lt 40 -and (Get-Process glazewm, glazewm-watcher -ErrorAction SilentlyContinue); $i++) {
    Start-Sleep -Milliseconds 500
  }
  Start-Sleep -Seconds 2  # deixa o vigia do GlazeWM fazer a parte dele primeiro
}

Add-Type @"
using System; using System.Collections.Generic; using System.Diagnostics; using System.Runtime.InteropServices; using System.Text;
[ComImport, Guid("6D5140C1-7436-11CE-8034-00AA006009FA"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IServiceProviderX { [PreserveSig] int QueryService(ref Guid s, ref Guid i, [MarshalAs(UnmanagedType.IUnknown)] out object o); }
[ComImport, Guid("372E1D3B-38D3-42E4-A15B-8AB2B178F513"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IApplicationViewX { void m1(); void m2(); void m3(); void m4(); void m5(); void m6(); void m7(); void m8(); void m9(); [PreserveSig] int SetCloak(uint t, int f); }
[ComImport, Guid("1841c6d7-4f9d-42c0-af41-8747538f10e5"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IApplicationViewCollectionX { void m1(); void m2(); void m3(); [PreserveSig] int GetViewForHwnd(IntPtr h, out IApplicationViewX v); }
public static class Uncloaker {
  [DllImport("dwmapi.dll")] static extern int DwmGetWindowAttribute(IntPtr h, int a, out int v, int s);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
  [DllImport("user32.dll")] static extern IntPtr GetWindow(IntPtr h, uint cmd);
  [DllImport("user32.dll")] static extern int GetWindowLong(IntPtr h, int i);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr l);

  // Processos/classes do próprio Windows que estão escondidos de propósito.
  static readonly HashSet<string> SkipProcess = new HashSet<string>(StringComparer.OrdinalIgnoreCase) {
    "explorer", "ShellExperienceHost", "StartMenuExperienceHost", "SearchHost", "SearchApp",
    "TextInputHost", "ApplicationFrameHost", "SystemSettings", "LockApp", "ShellHost",
    "WidgetBoard", "Widgets", "PhoneExperienceHost", "zebar", "msedgewebview2" };
  static readonly HashSet<string> SkipClass = new HashSet<string>(StringComparer.OrdinalIgnoreCase) {
    "Windows.UI.Core.CoreWindow", "ApplicationFrameWindow", "Shell_TrayWnd", "Progman", "WorkerW" };

  public static List<string> Run() {
    var log = new List<string>();
    var sp = (IServiceProviderX)Activator.CreateInstance(Type.GetTypeFromCLSID(new Guid("C2F03A33-21F5-47FA-B4BB-156362A2F239")));
    Guid g = typeof(IApplicationViewCollectionX).GUID; object o;
    if (sp.QueryService(ref g, ref g, out o) != 0) { log.Add("sem IApplicationViewCollection"); return log; }
    var views = (IApplicationViewCollectionX)o;
    EnumWindows((h, l) => {
      int cloak; DwmGetWindowAttribute(h, 14, out cloak, 4);
      if (cloak != 2 || !IsWindowVisible(h)) return true;             // 2 = escondida pela shell
      if (GetWindow(h, 4) != IntPtr.Zero) return true;                 // GW_OWNER: só janelas principais
      if ((GetWindowLong(h, -20) & 0x80) != 0) return true;            // WS_EX_TOOLWINDOW
      var t = new StringBuilder(200); GetWindowText(h, t, 200); if (t.Length == 0) return true;
      var c = new StringBuilder(100); GetClassName(h, c, 100); if (SkipClass.Contains(c.ToString())) return true;
      int pid; GetWindowThreadProcessId(h, out pid); string name = "";
      try { name = Process.GetProcessById(pid).ProcessName; } catch { return true; }
      if (SkipProcess.Contains(name)) return true;
      IApplicationViewX v; int hr = views.GetViewForHwnd(h, out v);
      int r = (hr == 0 && v != null) ? v.SetCloak(1, 0) : hr;
      // Só o nome da app no registo: os títulos podem ter dados pessoais.
      log.Add(name + " -> " + (r == 0 ? "mostrada" : "erro 0x" + r.ToString("X")));
      return true; }, IntPtr.Zero);
    return log;
  }
}
"@

$log = [Uncloaker]::Run()
$out = Join-Path $PSScriptRoot '.uncloak.log'
$lines = @("$(Get-Date -Format 's') janelas recuperadas: $($log.Count)") + $log
Set-Content -Path $out -Value $lines -Encoding UTF8
$lines
