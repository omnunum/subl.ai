import { createSignal } from 'solid-js';

function PlayPauseButton(props) {
  const [isPlaying, setIsPlaying] = createSignal(false);

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying());
  };

  return (
    <>
      <button onClick={togglePlayPause}>
        {isPlaying() ? <i class="fas fa-pause"></i> : <i class="fas fa-play"></i>}
      </button>
      <audio
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
        src={props.src}
      ></audio>
    </>
  );
}

export default PlayPauseButton;
