
let audioContext = null;
let audioUnlocked = false;

function getAudioContext() {
  if (typeof window === "undefined") return null;

  const AudioContextClass =
    window.AudioContext || window.webkitAudioContext;

  if (!AudioContextClass) return null;

  if (!audioContext) {
    audioContext = new AudioContextClass();
  }

  return audioContext;
}

// Unlock audio after the user's first interaction.
export function unlockCompletionSound() {
  const context = getAudioContext();
  if (!context) return;

  if (context.state === "suspended") {
    context.resume()
      .then(() => {
        audioUnlocked = context.state === "running";
      })
      .catch(() => {});
  } else {
    audioUnlocked = context.state === "running";
  }
}

// Play a soft two-note completion chime.
export function playCompletionSound() {
  const context = getAudioContext();
  if (!context) return;

  const play = () => {
    const now = context.currentTime;

    [880, 1174.66].forEach((frequency, index) => {
      const oscillator = context.createOscillator();
      const gain = context.createGain();

      const start = now + index * 0.14;

      oscillator.type = "sine";
      oscillator.frequency.setValueAtTime(frequency, start);

      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.exponentialRampToValueAtTime(
        0.12,
        start + 0.025
      );
      gain.gain.exponentialRampToValueAtTime(
        0.0001,
        start + 0.42
      );

      oscillator.connect(gain);
      gain.connect(context.destination);

      oscillator.start(start);
      oscillator.stop(start + 0.44);
    });
  };

  if (context.state === "running") {
    play();
    return;
  }

  context.resume()
    .then(() => {
      if (
        context.state === "running" &&
        (audioUnlocked || document.hasFocus())
      ) {
        play();
      }
    })
    .catch(() => {});
}
