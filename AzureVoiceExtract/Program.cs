using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;

namespace AzureVoiceExtract
{
    class Program
    {
        static string assembly_path = Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location);
        enum SettingIndex
        {
            ExampleAudio = 0,
            SourceDir,
            ResDir
        }
        static Dictionary<SettingIndex, string> settings = new Dictionary<SettingIndex, string>()
        {
            {SettingIndex.ExampleAudio, @"example.wav"},
            {SettingIndex.SourceDir, assembly_path + Path.DirectorySeparatorChar + @"src"},
            {SettingIndex.ResDir, assembly_path + Path.DirectorySeparatorChar + @"res"}
        };

        static async Task Main(string[] args)
        {
            if (args.Length == 0) {
                Console.WriteLine("Usage: <subscription key> [example audio] [source path] [result path]");
                Console.WriteLine("<subscription key> - MS Azure Congitive Services Speech subsriction key");
                Console.WriteLine("[example audio] - example audio, default example.wav in the program directory");
                Console.WriteLine("[source path]  - path to audio files to check, default 'src' in the program directory");
                Console.WriteLine("[result path]  - path to result audio files, default 'res' in the program directory");
                return;
            }
            string subscriptionKey = args[0];
            
            if (args.Length > 1) {
                string[] parameters = new string[args.Length - 1];
                for(int i = 0; i < parameters.Length; ++i)
                    settings[(SettingIndex)i] = args[i+1];
            }

            string region = "westus";
            var config = SpeechConfig.FromSubscription(subscriptionKey, region);

            // persist profileMapping if you want to store a record of who the profile is
            var profileMapping = new Dictionary<string, string>();
            await VerificationEnroll(config, profileMapping);

            Console.WriteLine($"Verified");
        }

        public static async Task VerificationEnroll(SpeechConfig config, Dictionary<string, string> profileMapping)
        {
            using (var client = new VoiceProfileClient(config))
            using (var profile = await client.CreateProfileAsync(VoiceProfileType.TextIndependentVerification, "en-us"))
            {
                using (var audioInput = AudioConfig.FromWavFileInput(settings[SettingIndex.ExampleAudio]))
                {
                    Console.WriteLine($"Enrolling profile id {profile.Id}.");
                    // give the profile a human-readable display name
                    profileMapping.Add(profile.Id, "Test speaker");

                    VoiceProfileEnrollmentResult result = null;
                    result = await client.EnrollProfileAsync(profile, audioInput);

                    if (result != null)
                    {
                        if (result.Reason == ResultReason.EnrolledVoiceProfile)
                        {
                            string[] files = Directory.GetFiles(settings[SettingIndex.SourceDir], "*.wav", SearchOption.TopDirectoryOnly);
                            
                            foreach (string file in files)
                            {
                                await SpeakerVerify(config, profile, profileMapping, file);
                            }
                        }
                        else if (result.Reason == ResultReason.Canceled)
                        {
                            var cancellation = VoiceProfileEnrollmentCancellationDetails.FromResult(result);
                            Console.WriteLine($"CANCELED {profile.Id}: ErrorCode={cancellation.ErrorCode} ErrorDetails={cancellation.ErrorDetails}");
                        }
                        await client.DeleteProfileAsync(profile);
                    }
                    else
                    {
                        Console.WriteLine("Profile enrollment error");
                    }
                }
            }
        }

        public static async Task SpeakerVerify(SpeechConfig config, VoiceProfile profile, Dictionary<string, string> profileMapping, string file)
        {
            var model = SpeakerVerificationModel.FromProfile(profile);

            Console.WriteLine($"Veryifying {file} ...");
            try
            {
                var speakerRecognizer = new SpeakerRecognizer(config, AudioConfig.FromWavFileInput(file));
                var result = await speakerRecognizer.RecognizeOnceAsync(model);
                Console.WriteLine($"Verified voice profile for speaker {profileMapping[result.ProfileId]}, score is {result.Score}");
                if (result.Score >= 0.5)
                {
                    File.Copy(file, Path.Combine(settings[SettingIndex.ResDir], Path.GetFileName(file)), true);
                }
            }
            catch(Exception ex)
            {
                Console.WriteLine("Exception caught: " + ex.Message);
            }
        }
    }
}
