import React from "react";
import PropTypes from "prop-types";

export default function Likes({ numLikes, toggleLike, likeStatus }) {
  const singular = numLikes === 1;
  return (
    <div>
      <div>
        <button
          type="button"
          data-testid="like-unlike-button"
          onClick={toggleLike}
        >
          {likeStatus ? "unlike" : "like"}
        </button>
      </div>
      {numLikes} <span>{singular ? "like" : "likes"}</span>
    </div>
  );
}
Likes.propTypes = {
  numLikes: PropTypes.number.isRequired,
  toggleLike: PropTypes.func.isRequired,
  likeStatus: PropTypes.bool.isRequired,
};
