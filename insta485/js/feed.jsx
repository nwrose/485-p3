import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

export default function Feed({ url }) {
  const [postArr, setPostArr] = useState([]);
  const [pageNext, setPageNext] = useState(url);
  const [hasMore, setHasMore] = useState(true);
  const [trigger, setTrigger] = useState(true);

  function getNextPage() {
    console.log(`getting next page at: ${pageNext}`);
    setTrigger(!trigger);
  }

  useEffect(() => {
    let ignoreStaleRequest = false;

    // Call Rest API to get the list of posts on feed
    fetch(pageNext, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (!ignoreStaleRequest) {
          const posts = postArr;
          setPostArr([...posts, ...data.results]);
          setPageNext(data.next);
          setHasMore(data.next !== "");
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // Cleanup function --> refer to post.jsx desc
      //    for more info about ignoreStaleRequest
      ignoreStaleRequest = true;
    };
  }, [url, trigger]);

  // Render the f
  return (
    <div id="feed">
      <InfiniteScroll
        dataLength={postArr.length} // This is important field to render the next data
        next={() => getNextPage()}
        hasMore={hasMore}
        loader={<h4>Loading...</h4>}
        endMessage={
          <p style={{ textAlign: "center" }}>
            <b>All Posts Loaded</b>
          </p>
        }
      >
        {postArr.map((post) => (
          <Post key={post.postid} url={`/api/v1/posts/${post.postid}/`} />
        ))}
      </InfiniteScroll>
    </div>
  );
}
//            {console.log('rendering the feed!')}
//
Feed.propTypes = {
  url: PropTypes.string.isRequired,
};
