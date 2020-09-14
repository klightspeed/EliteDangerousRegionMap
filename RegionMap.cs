using System;
using System.Net;
using System.Text.Json;

namespace EliteDangerousRegionMap
{
    public static partial class RegionMap
    {
        private class EDSMSystem
        {
            public string name { get; set; }
            public long id64 { get; set; }
            public EDSMSystemCoords coords { get; set; }
        }

        private class EDSMSystemCoords
        {
            public double x { get; set; }
            public double y { get; set; }
            public double z { get; set; }
        }

        private const double x0 = -49985;
        private const double y0 = -40985;
        private const double z0 = -24105;

        public static (int, string) FindRegion(double x, double y, double z)
        {
            var px = (int)((x - x0) * 83 / 4096);
            var pz = (int)((z - z0) * 83 / 4096);

            if (px < 0 || pz < 0 || pz >= RegionMapLines.Length)
            {
                return default;
            }
            else
            {
                var row = RegionMapLines[pz];
                var rx = 0;
                var pv = 0;

                foreach (var (rl, rv) in row)
                {
                    if (px < rx + rl)
                    {
                        pv = rv;
                        break;
                    }
                    else
                    {
                        rx += rl;
                    }
                }

                if (pv == 0)
                {
                    return default;
                }
                else
                {
                    return (pv, RegionNames[pv]);
                }
            }
        }

        private static void Main(string[] args)
        {
            if (args.Length == 0)
            {
	    	var exe = System.Reflection.Assembly.GetExecutingAssembly().Location;
                Console.WriteLine($"Usage: {exe} \"System 1\" [...]");
                return;
            }

            foreach (var name in args)
            {
                var url = $"https://www.edsm.net/api-v1/systems?systemName={Uri.EscapeDataString(name)}&coords=1&showId=1";
                var client = new WebClient();
                var jsonstr = client.DownloadString(url);
                var systems = JsonSerializer.Deserialize<EDSMSystem[]>(jsonstr);

                foreach (var system in systems)
                {
                    int regionid = 0;
                    string regionname = null;

                    if (system.coords != null)
                    {
                        double x = system.coords.x;
                        double y = system.coords.y;
                        double z = system.coords.z;

                        (regionid, regionname) = FindRegion(x, y, z);
                        if (regionid != 0)
                        {
                            Console.WriteLine($"System {system.name} at ({x},{y},{z}) is in region {regionid} ({regionname})");
                        }
                        else
                        {
                            Console.WriteLine($"System {system.name} at ({x},{y},{z}) is outside the region map");
                        }
                    }

                    if (system.id64 != 0)
                    {
                        int masscode = (int)(system.id64 & 7);
                        double x = (((system.id64 >> (30 - masscode * 2)) & (0x3FFF >> masscode)) << masscode) * 10 + x0;
                        double y = (((system.id64 >> (17 - masscode)) & (0x1FFF >> masscode)) << masscode) * 10 + y0;
                        double z = (((system.id64 >> 3) & (0x3FFF >> masscode)) << masscode) * 10 + z0;

                        var (regionid2, regionname2) = FindRegion(x, y, z);

                        if (regionid2 != regionid)
                        {
                            if (regionid2 != 0)
                            {
                                Console.WriteLine($"Boxel of system {system.name} at ({x},{y},{z}) is in region {regionid2} ({regionname2})");
                            }
                            else
                            {
                                Console.WriteLine($"Boxel of system {system.name} at ({x},{y},{z}) is outside the region map");
                            }
                        }
                    }
                }
            }
        }
    }
}
