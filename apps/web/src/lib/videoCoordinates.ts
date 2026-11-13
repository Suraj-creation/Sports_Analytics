/** Relate raw analysis pixels to the video's object-fit: contain presentation.
 * Browser video dimensions may include sample-aspect-ratio correction; model,
 * court and calibration coordinates still refer to the coded analysis pixels.
 */
export interface VideoViewport {
  left: number;
  top: number;
  width: number;
  height: number;
  scaleX: number;
  scaleY: number;
}

export function videoViewport(
  containerWidth: number,
  containerHeight: number,
  presentationWidth: number,
  presentationHeight: number,
  analysisWidth: number,
  analysisHeight: number,
): VideoViewport | null {
  if (
    ![
      containerWidth,
      containerHeight,
      presentationWidth,
      presentationHeight,
      analysisWidth,
      analysisHeight,
    ].every((value) => Number.isFinite(value) && value > 0)
  )
    return null;
  const scale = Math.min(containerWidth / presentationWidth, containerHeight / presentationHeight);
  const width = presentationWidth * scale;
  const height = presentationHeight * scale;
  return {
    left: (containerWidth - width) / 2,
    top: (containerHeight - height) / 2,
    width,
    height,
    scaleX: width / analysisWidth,
    scaleY: height / analysisHeight,
  };
}

/** A pointer in the video's container becomes a raw analysis point; bars are not image evidence. */
export function analysisPoint(x: number, y: number, viewport: VideoViewport): [number, number] | null {
  const localX = x - viewport.left;
  const localY = y - viewport.top;
  if (
    !Number.isFinite(x) ||
    !Number.isFinite(y) ||
    localX < 0 ||
    localY < 0 ||
    localX > viewport.width ||
    localY > viewport.height
  )
    return null;
  return [localX / viewport.scaleX, localY / viewport.scaleY];
}
