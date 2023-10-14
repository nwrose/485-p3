import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import InfoBar from "./infoBar"
import PostComments from "./postComments"
import Likes from "./likes"

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [timestamp, setTimestamp] = useState("");
  const [postid, setPostid] = useState(-1);
  const [commentsInfo, setCommentInfo] = useState([])
  const [numLikes, setNumLikes] = useState(-1)
  const [likeStatus, setLikeStatus] = useState(true)
  const [rmLikeUrl, setrmLikeUrl] = useState("")

  //Do the like button function stuff

  function doubleClick(){
    let double_ignoreStaleRequest = false;
    if(!likeStatus){
        fetch(`/api/v1/likes/?postid=${postid}`, {credentials: "same-origin", method: "POST"})
        .then((response) => {
            if(!response.ok) throw Error(response.statusText);
            return response.json()
        })
        .then((data) => {
            if (!double_ignoreStaleRequest){
                setNumLikes(numLikes + 1);
                setrmLikeUrl(data.url);
                setLikeStatus(true);
            }
        })
        .catch((error) => console.log(error));
        return () => {
            double_ignoreStaleRequest = true;
        }    }
  }

  function toggleLike() {
    let like_ignoreStaleRequest = false;
    if (likeStatus){
        fetch(rmLikeUrl, { credentials: "same-origin", method:'DELETE'})
        .then((response) => {
            if(!response.ok) throw Error(response.statusText);
        })
        .then(() => {
            if(!like_ignoreStaleRequest){
                setNumLikes(numLikes - 1);
                setrmLikeUrl("");
                setLikeStatus(false);
            }
        })  
        .catch((error) => console.log(error));
        return () => {
            like_ignoreStaleRequest = true;
        }
    }
    else{
        fetch(`/api/v1/likes/?postid=${postid}`, {credentials: "same-origin", method: "POST"})
        .then((response) => {
            if(!response.ok) throw Error(response.statusText);
            return response.json()
        })
        .then((data) => {
            if (!like_ignoreStaleRequest){
                setNumLikes(numLikes + 1);
                setrmLikeUrl(data.url);
                setLikeStatus(true);
            }
        })
        .catch((error) => console.log(error));
        return () => {
            like_ignoreStaleRequest = true;
        }
    }
  }


  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setTimestamp(data.created);
          setOwnerImgUrl(data.ownerImgUrl);
          setPostid(data.postid);
          setCommentInfo(data.comments);
          setNumLikes(data.likes.numLikes);
          setLikeStatus(data.likes.lognameLikesThis);
          setrmLikeUrl(data.likes.url)
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  // Render post image and post owner
  return (
    <div className="post">
        {console.log('rendering a post!')}
        <InfoBar owner={owner} timestamp={timestamp} ownerImgUrl={ownerImgUrl} postid={postid}/>
        <img src={imgUrl} alt="post_image" onDoubleClick={() => doubleClick()}/>
        <Likes numLikes={numLikes} toggleLike={toggleLike} likeStatus={likeStatus}/>
        <PostComments commentsInfo={commentsInfo}/>
    </div>
  );
}


Post.propTypes = {
  url: PropTypes.string.isRequired,
};  