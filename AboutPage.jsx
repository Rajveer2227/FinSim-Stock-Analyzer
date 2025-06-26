import React from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import videoFile from "../assets/finsimintro.mp4"; // Replace with your actual video file path
import { motion } from "framer-motion";
import { FaStar, FaRegStar, FaStarHalfAlt } from 'react-icons/fa';

const AboutPage = () => {
  return (
    <div className="about-page">
      <Container className="mt-5">
      <Row className="text-center mb-4">
  <Col>
    <motion.h1
      className="text-white"
      initial={{ opacity: 0, y: -40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1 }}
    >
     <b> About Us</b>
    </motion.h1>
    <p className="lead text-white">Learn more about FinSim and our mission.</p>
  </Col>
</Row>

        
        <Row className="mb-5">
          <Col md={6}>
            <Card>
              <Card.Body>
                <Card.Title> <FaStar /> <b>Our Mission</b></Card.Title>
                <Card.Text>
                At FinSim, our mission is to make financial education accessible and engaging by offering a realistic stock trading simulation. We aim to equip users with real-time tools, analytics, and market insights to help them practice, learn, and grow.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>

          <Col md={6}>
            <Card>
              <Card.Body>
                <Card.Title> <FaStar /> <b>Our Vision</b></Card.Title>
                <Card.Text>
                Our vision is to become the leading platform for financial learning and market simulation, empowering students and aspiring traders to make smarter investment decisions through hands-on experience and interactive learning environments.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Video Section */}
             {/* Video Section */}
      <Row className="text-center mt-5 mb-5"> {/* Added mb-5 for space before footer */}
        <Col>
        <h2 className="text-white"> <b>What We Provide</b></h2>
<p className="lead text-white">Watch this quick video to learn about our features.</p>

          <div className="video-wrapper">
          <motion.video
  className="about-video"
  autoPlay
  muted
  loop
  playsInline
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 1 }}
>
  <source src={videoFile} type="video/mp4" />
  Your browser does not support the video tag.
</motion.video>

          </div>
        </Col>
      </Row>

      </Container>

      {/* Inline CSS */}
     
      
       <style>{`
  .about-page {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364); /* Light grey-blue */
    min-height: 100vh; /* Full height if content is less */
    padding-top: 20px;
    padding-bottom: 20px;
  }

  .about-video {
    width: 80%;
    max-width: 720px;
    border: 4px solid #0d6efd;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    margin-top: 20px;
  }

  .video-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
  }
`}</style>

    
    </div>
  );
};

export default AboutPage;
